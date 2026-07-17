---
doc_type: feature-design
feature: 2026-07-17-hermes-tavern-phase506-attention-status-sync-through-phase505
status: approved
implementation_ready: true
date: "2026-07-17"
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 506 attention status sync through accepted Phase 505."
tags: [hermes-tavern, codestable, attention, status-sync, documentation, tests, phase506]
---

# Phase 506 Attention Status Sync

## Scope

Advance the sole attention current-status record and its focused static contract from Phase 505 to Phase 506. This slice is documentation and static-test metadata only.

## Exact Contract

- Set the current prefix to `Current status (2026-06-18): All phases 1-506 accepted`.
- Append `Phase 506 attention status sync through Phase 505` exactly once after the Phase 505 label.
- Preserve the date, status-line placement, history, label order, and the Phase 121-167 aggregate.
- Require 339 ordered labels, `range(168, 507)`, rotated stale prefix/marker guards, a dynamically built stale old-range guard, and a suffix ending with Phase 502 through Phase 506.

## Boundaries

Only `design/codestable/attention.md`, `tests/test_hermes_tavern_codestable_status.py`, and this feature's design/checklist may change. Do not modify runtime, auth, gateway, provider, Radar, README, root design, architecture, other tests, or lifecycle artifacts.

## Lifecycle

This is S1 implementation only. The design is approved and implementation-ready; the checklist remains non-final with parent verification required and incomplete. Do not create `acceptance.md`, mark the feature accepted, commit, or push.

## Verification

- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-17-hermes-tavern-phase506-attention-status-sync-through-phase505/2026-07-17-hermes-tavern-phase506-attention-status-sync-through-phase505-design.md --require doc_type --require status --require feature --require summary --require tags`
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-07-17-hermes-tavern-phase506-attention-status-sync-through-phase505/2026-07-17-hermes-tavern-phase506-attention-status-sync-through-phase505-checklist.yaml --require doc_type --require status --require feature`
- `python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`
