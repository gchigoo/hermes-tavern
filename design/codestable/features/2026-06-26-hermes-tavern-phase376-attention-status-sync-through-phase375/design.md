---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase376-attention-status-sync-through-phase375
title: "Phase 376 attention/status sync through Phase 375"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 376 attention/status sync through accepted Phase 375."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase376]
---

# Phase 376 attention/status sync through Phase 375

## Background / Current Status

Phase 375 is accepted:

`design/codestable/features/2026-06-26-hermes-tavern-phase375-attention-status-sync-through-phase374/acceptance.md`

Inspected baseline:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-375 accepted`.
- Terminal suffix is `Phase 373 attention status sync through Phase 372, Phase 374 attention status sync through Phase 373, and Phase 375 attention status sync through Phase 374.`
- `tests/test_hermes_tavern_codestable_status.py` has `CURRENT_STATUS_PREFIX` pinned to Phase 375.
- The focused status test currently has stale prefix and markers for Phase 374.
- The focused status test currently uses `phase_range = range(168, 376)` and live aggregate string `range(168, 376)`.
- The focused status test already includes the split stale aggregate guard for `range(168, 375)`.

Range note: Phase 376 must advance the live range to `range(168, 377)` and add a split stale guard for `range(168, 376)`.

## Goals

- Controller materializes the Phase 376 design/checklist artifacts before executor S1.
- Advance `design/codestable/attention.md` exactly one status tick from 1-375 to 1-376.
- Append `Phase 376 attention status sync through Phase 375` exactly once.
- Update the focused status regression to guard the Phase 376 live status contract.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 376 label.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No root docs, architecture, roadmap, requirements, or compound updates.
- No service lifecycle commands, cache artifacts, staging, commits, or pushes.
- No `acceptance.md` creation during executor S1.
- No executor edits to design/checklist artifacts.
- No Phase 377 work.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No provider-safety, content, RP, adult-fiction behavior, or minor-related behavior changes.

## S1/S2 Boundary

Controller pre-S1 owns artifact materialization for:

- `design/codestable/features/2026-06-26-hermes-tavern-phase376-attention-status-sync-through-phase375/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase376-attention-status-sync-through-phase375/checklist.yaml`

Executor S1 may edit only exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

Executor S1 must not create `acceptance.md`, edit design/checklist artifacts, stage, commit, push, touch Phase 377, or touch prohibited runtime/source/plugin/provider/gateway/CLI/config/dependency/root docs/architecture/roadmap/requirements/compound/build/service lifecycle/cache paths.

Controller S2 owns verification, `acceptance.md` creation, and final checklist status updates after verification.

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-375 accepted` -> `All phases 1-376 accepted`.
- Move `and` from Phase 375 to Phase 376.
- Append `Phase 376 attention status sync through Phase 375` after Phase 375.
- Final suffix must be `Phase 374 attention status sync through Phase 373, Phase 375 attention status sync through Phase 374, and Phase 376 attention status sync through Phase 375.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX` -> `Current status (2026-06-18): All phases 1-376 accepted`.
- `STALE_STATUS_PREFIX` -> `Current status (2026-06-18): All phases 1-375 accepted`.
- `STALE_PHASE_MARKER` -> `1-375`.
- `STALE_PHASE_MARKER_EN_DASH` -> `1–375`.
- Append `Phase 376 attention status sync through Phase 375` to `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX` -> `Phase 374 attention status sync through Phase 373, Phase 375 attention status sync through Phase 374, and Phase 376 attention status sync through Phase 375.`
- `phase_range = range(168, 377)`.
- `aggregate_range = "range(168, 377)"`.
- Add split stale guard: `stale_aggregate_range_376 = "".join(["range(168, ", "37", "6", ")"])`.
- Include `stale_aggregate_range_376` in the stale assertion tuple.
- Ensure the contiguous literal `range(168, 376)` does not remain outside split string construction.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-26-hermes-tavern-phase376-attention-status-sync-through-phase375/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-26-hermes-tavern-phase376-attention-status-sync-through-phase375/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- `test ! -e design/codestable/features/2026-06-26-hermes-tavern-phase376-attention-status-sync-through-phase375/acceptance.md`
- `git diff --check`

## Parent-Controller S2 Ownership

- This phase is an S1/non-final status-sync slice.
- Parent controller remains responsible for S2 acceptance creation, final YAML/static checks, full-suite verification when feasible, and final state transition to `accepted`.
- Executor must leave `acceptance.md` absent and preserve full S1/non-final handoff state.
