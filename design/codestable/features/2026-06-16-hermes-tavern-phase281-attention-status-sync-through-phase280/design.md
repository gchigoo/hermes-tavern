---
doc_type: feature-design
status: approved
implementation_ready: true
feature: "2026-06-16-hermes-tavern-phase281-attention-status-sync-through-phase280"
date: "2026-06-16"
created: "2026-06-16"
updated: "2026-06-16"
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 280, without changing runtime/source behavior,
  Hermes-native plugin architecture, provider safety behavior, provider settings,
  credentials, or SillyTavern assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 281: CodeStable Attention Status Sync Through Phase 280

## Exact S1 Contract

- `design/codestable/attention.md` current status starts with
  `Current status (2026-06-16): All phases 1-280 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` updates
  `CURRENT_STATUS_PREFIX` and `STALE_STATUS_PREFIX` to:
  - `Current status (2026-06-16): All phases 1-280 accepted`
  - `Current status (2026-06-16): All phases 1-279 accepted`
- Preserve valid internal range `Phase 121-167`.
- Preserve all existing Phase 168 through Phase 279 labels and append exactly:
  `Phase 280 attention status sync through Phase 279`.
- The current-status bullet ends with:
  `Phase 278 attention status sync through Phase 277, Phase 279 attention status sync through Phase 278, and Phase 280 attention status sync through Phase 279.`
- Reject stale terminal accepted markers/prefixes for
  `1-279` and `1–279`.
- `phase_range = range(168, 281)` in focused regression; reject stale
  `range(168, 279)` and `range(168, 280)` via split-string construction.

## Scope

S1 may change only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-16-hermes-tavern-phase281-attention-status-sync-through-phase280/design.md`
- `design/codestable/features/2026-06-16-hermes-tavern-phase281-attention-status-sync-through-phase280/checklist.yaml`

## Non-Goals

No runtime/source/provider/plugin behavior changes. No edits to provider safety,
prompt behavior, imports/exports/schema, credentials, service lifecycle, or
SillyTavern assets. No acceptance.md updates in this pass.
