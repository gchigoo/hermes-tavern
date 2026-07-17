---
doc_type: feature-design
feature: 2026-07-17-hermes-tavern-phase508-attention-status-sync-through-phase507
status: approved
implementation_ready: true
date: "2026-07-17"
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 508 attention status sync through accepted Phase 507."
tags: [hermes-tavern, codestable, attention, status-sync, documentation, tests, phase508]
---

# Phase 508 Attention Status Sync

## Scope

Advance the sole attention current-status record and focused static contract from Phase 507 to Phase 508.

## Exact Contract

- Set `Current status (2026-06-18): All phases 1-508 accepted`.
- Append `Phase 508 attention status sync through Phase 507` exactly once after Phase 507.
- Preserve history, ordering, date, and the Phase 121-167 aggregate.
- Require 341 ordered labels, `range(168, 509)`, rotated stale guards, and an exact Phase 504-508 suffix.

## Boundaries

Only attention, the focused status test, and this feature design/checklist may change in S1. Do not modify runtime, plugins, core Hermes files, auth, gateway, provider, Radar, README, root design, architecture, other tests, or lifecycle artifacts.

## Lifecycle

This is S1 only. Keep the checklist non-final and do not create acceptance before parent verification.

## Verification

- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-17-hermes-tavern-phase508-attention-status-sync-through-phase507/2026-07-17-hermes-tavern-phase508-attention-status-sync-through-phase507-design.md --require doc_type --require status --require feature --require summary --require tags`
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-07-17-hermes-tavern-phase508-attention-status-sync-through-phase507/2026-07-17-hermes-tavern-phase508-attention-status-sync-through-phase507-checklist.yaml --require doc_type --require status --require feature`
- `python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`