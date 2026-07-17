---
doc_type: feature-design
feature: 2026-07-17-hermes-tavern-phase505-attention-status-sync-through-phase504
status: approved
implementation_ready: true
date: "2026-07-17"
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 505 attention status sync through accepted Phase 504."
tags: [hermes-tavern, codestable, attention, status-sync, documentation, tests, phase505]
---

# Phase 505 Attention Status Sync

## Scope

Advance the single attention current-status record and its focused static test from Phase 504 to Phase 505. This is documentation and static-test metadata only.

## Exact Contract

- Set the current prefix to `Current status (2026-06-18): All phases 1-505 accepted`.
- Append `Phase 505 attention status sync through Phase 504` exactly once, after the Phase 504 label.
- Preserve the status-line placement, all existing labels, and the Phase 121-167 aggregate.
- Update the focused prefix/stale markers/labels/suffix/ranges to Phase 505, including `range(168, 506)` and the Phase 505 stale aggregate guards.

## Boundaries

Only `design/codestable/attention.md`, `tests/test_hermes_tavern_codestable_status.py`, and this feature's design/checklist may change. Do not modify runtime, plugin, README, architecture, requirements, roadmap, or other product documentation.

## Lifecycle

This is S1 implementation only. Keep the checklist implemented but non-final and pending parent verification. Do not create `acceptance.md`, mark the feature accepted, commit, or push.

## Verification

- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-17-hermes-tavern-phase505-attention-status-sync-through-phase504/2026-07-17-hermes-tavern-phase505-attention-status-sync-through-phase504-design.md --require doc_type --require status --require feature --require summary --require tags`
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-07-17-hermes-tavern-phase505-attention-status-sync-through-phase504/2026-07-17-hermes-tavern-phase505-attention-status-sync-through-phase504-checklist.yaml --require doc_type --require status --require feature`
- `python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`
