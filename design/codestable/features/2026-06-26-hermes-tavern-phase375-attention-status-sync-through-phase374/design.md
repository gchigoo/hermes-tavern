---
doc_type: feature-design
title: "Phase 375 attention status sync through Phase 374"
feature: 2026-06-26-hermes-tavern-phase375-attention-status-sync-through-phase374
status: approved
implementation_ready: true
date: "2026-06-26"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 375 attention status sync through accepted Phase 374."
tags:
  - hermes-tavern
  - codestable
  - attention
  - status-sync
  - docs
  - tests
  - phase375
  - company-boost
  - parent-handoff
---

# Phase 375 attention status sync through Phase 374

## Background / current state
- Baseline is branch `main` at commit `514449e`.
- Phase 374 is accepted and currently synced through
  `design/codestable/features/2026-06-26-hermes-tavern-phase374-attention-status-sync-through-phase373`.
- This slice is S1 status-sync only, bounded to docs/tests and not an implementation execution slice.
- `acceptance.md` for this phase must remain absent during S1.

## Goals
- Extend attention/status tracking records from Phase 374 acceptance to Phase 375 acceptance text in
  `design/codestable/attention.md`.
- Extend status assertions in
  `tests/test_hermes_tavern_codestable_status.py` to require Phase 375 labels and updated stale guards.
- Create `design.md` and `checklist.yaml` for Phase 375 with the exact required metadata and handoff state.

## Non-goals
- No runtime or provider logic changes.
- No plugin, gateway, CLI, or dependency graph changes.
- No acceptance finalization artifacts (`acceptance.md`) during S1.
- No architectural, safety, adult, or minors behavior changes.

## Allowed scope
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase375-attention-status-sync-through-phase374/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase375-attention-status-sync-through-phase374/checklist.yaml`

## Exact status contract
- Single current status line in `attention.md` must be:
  - Prefix: `Current status (2026-06-18): All phases 1-375 accepted`
  - Suffix: `Phase 373 attention status sync through Phase 372, Phase 374 attention status sync through Phase 373, and Phase 375 attention status sync through Phase 374.`
- `tests/test_hermes_tavern_codestable_status.py` must assert:
  - `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-375 accepted"`
  - `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-374 accepted"`
  - `STALE_PHASE_MARKER = "1-374"`
  - `STALE_PHASE_MARKER_EN_DASH = "1–374"`
  - `FINAL_STATUS_SUFFIX` exactly matching the suffix above.
  - `phase_range = range(168, 376)`
  - `aggregate_range = "range(168, 376)"`
  - `stale_aggregate_range_375 = "".join(["range(168, ", "37", "5", ")"])`
  - `stale_aggregate_range_375` included in stale assertion tuple.
  - No contiguous literal `range(168, 375)` remains in source except split pieces of `stale_aggregate_range_375`.

## S1 checklist state
- S1 executor status: `implemented`.
- Checks C1–C12 are marked completed for: design materialization, checklist materialization, status line updates, test updates, and stale-guard updates.
- Acceptance artifact creation is prohibited in S1.
- Commit/push/stage operations are prohibited.

## Verification gates
1. `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-26-hermes-tavern-phase375-attention-status-sync-through-phase374/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
2. `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-26-hermes-tavern-phase375-attention-status-sync-through-phase374/checklist.yaml --yaml-only`
3. `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
4. `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
5. `test ! -e design/codestable/features/2026-06-26-hermes-tavern-phase375-attention-status-sync-through-phase374/acceptance.md`
6. `git diff --check`

## Parent-controller S2 ownership
- This phase is an S1/non-final status-sync slice.
- Parent controller remains responsible for S2:
  - acceptance artifact creation
  - final YAML/static checks requiring runtime and broader command scope
  - final state transition to `accepted`
- Executor must leave `acceptance.md` absent and preserve full `S1 only / non-final` handoff state.
