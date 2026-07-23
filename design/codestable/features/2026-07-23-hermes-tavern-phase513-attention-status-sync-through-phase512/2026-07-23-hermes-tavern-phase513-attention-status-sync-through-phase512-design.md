---
doc_type: feature-design
feature: 2026-07-23-hermes-tavern-phase513-attention-status-sync-through-phase512
status: approved
implementation_ready: true
bounded_phase: docs/static-test/status-only
parent_verification_status: pending_parent_verification
acceptance_state: pending_parent_verification
summary: Approved S1 design for Phase 513 attention status sync through accepted Phase 512.
tags: [codestable, status-sync, docs, static-test]
---

# Phase 513 Attention Status Sync

## Scope

Advance only the canonical attention current-status record and its focused static contract from Phase 512 to Phase 513; Phase 513 has no runtime or plugin behavior change.

## Exact Contract

- Set `Current status (2026-06-18): All phases 1-513 accepted`.
- Append `Phase 513 attention status sync through Phase 512` exactly once after Phase 512.
- Preserve history, ordering, date, and the Phase 121-167 aggregate.
- Require 346 ordered labels, `range(168, 514)`, stale guards for Phases 512/511/510/509, and the exact Phase 509-513 suffix.

## Constraints

Only attention, the focused status test, and this feature's design/checklist may change in S1. Do not modify Hermes core, plugin runtime, gateway, provider, auth, cron, Radar, README, architecture, or root design.

## Lifecycle

This is S1 only. Keep the checklist non-final. This bounded status-sync slice does not create an acceptance artifact; the parent controller records verification only in the existing checklist.

## Verification

- `python3 design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-23-hermes-tavern-phase513-attention-status-sync-through-phase512`
- `python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`
