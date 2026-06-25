---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase360-attention-status-sync-through-phase359
title: "Phase 360 attention/status sync through Phase 359"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 360 attention/status sync through accepted Phase 359."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase360]
---

# Phase 360 attention/status sync through Phase 359

## Background / Current Status

Phase 359 is accepted:

`design/codestable/features/2026-06-26-hermes-tavern-phase359-attention-status-sync-through-phase358/acceptance.md`

Controller-verified baseline:

- Repository status is clean.
- No Phase 360 feature directory exists.
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-359 accepted`.
- Terminal suffix is `Phase 357 attention status sync through Phase 356, Phase 358 attention status sync through Phase 357, and Phase 359 attention status sync through Phase 358.`
- `tests/test_hermes_tavern_codestable_status.py` has `CURRENT_STATUS_PREFIX` pinned to Phase 359.
- The focused status test currently has stale prefix and markers for Phase 358.
- The focused status test currently uses `phase_range = range(168, 360)` and live aggregate string `range(168, 360)`.
- The focused status test already includes the split stale aggregate guard for `range(168, 359)`.

Range note: Phase 360 must advance the live range to `range(168, 361)` and add a split stale guard for `range(168, 360)`.

## Goals

- Create the Phase 360 design/checklist artifacts as implementation-ready S1 handoff artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-359 to 1-360.
- Append `Phase 360 attention status sync through Phase 359` exactly once.
- Update the focused status regression to guard the Phase 360 live status contract.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 360 label.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No root docs, architecture, roadmap, requirements, or compound updates.
- No service lifecycle commands or dependency installation.
- No `acceptance.md` creation during executor S1.
- No executor staging, commits, or pushes.
- No Phase 361 work.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No provider-safety, content, RP, or adult-fiction behavior changes.

## S1/S2 Boundary

Executor S1 may edit only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase360-attention-status-sync-through-phase359/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase360-attention-status-sync-through-phase359/checklist.yaml`

Executor S1 must not create `acceptance.md`, stage, commit, push, or touch prohibited runtime/source/plugin/provider/gateway/CLI/config/dependency/root docs/architecture/roadmap/requirements/compound/build paths.

Controller S2 owns verification, `acceptance.md` creation, final checklist status updates, and any parent commit/push action after verification.

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-359 accepted` -> `All phases 1-360 accepted`
- Move `and` from Phase 359 to Phase 360.
- Append `Phase 360 attention status sync through Phase 359` after Phase 359.
- Final suffix must be `Phase 358 attention status sync through Phase 357, Phase 359 attention status sync through Phase 358, and Phase 360 attention status sync through Phase 359.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-359` -> `1-360`
- `STALE_STATUS_PREFIX`: `1-358` -> `1-359`
- `STALE_PHASE_MARKER`: `1-358` -> `1-359`
- `STALE_PHASE_MARKER_EN_DASH`: `1–358` -> `1–359`
- Add `"Phase 360 attention status sync through Phase 359"` to `REQUIRED_PHASE_LABELS`
- `FINAL_STATUS_SUFFIX`: `Phase 358 attention status sync through Phase 357, Phase 359 attention status sync through Phase 358, and Phase 360 attention status sync through Phase 359.`
- `phase_range`: `range(168, 360)` -> `range(168, 361)`
- Live `aggregate_range`: `"range(168, 360)"` -> `"range(168, 361)"`
- Add split stale guard `stale_aggregate_range_360 = "".join(["range(168, ", "36", "0", ")"])`
- Include `stale_aggregate_range_360` in the stale range assertion tuple.
- Do not leave a contiguous literal `range(168, 360)` in test source except where the current aggregate exact-string pattern explicitly requires it; the stale guard must be split.

## Structure Health

This is docs/static-test/status-only. No source structure, module boundary, dependency graph, runtime flow, architecture, roadmap, requirement, or compound document changes are involved. No microrefactor is allowed or useful for this slice.

## Acceptance Contract For Controller S2

- `attention.md` has exactly one current status line.
- Current status line starts with `Current status (2026-06-18): All phases 1-360 accepted`.
- Current status line contains `Phase 360 attention status sync through Phase 359` exactly once.
- Current status line preserves `Phase 121-167` and every explicit Phase 168 through Phase 360 label.
- Current status line ends with `Phase 358 attention status sync through Phase 357, Phase 359 attention status sync through Phase 358, and Phase 360 attention status sync through Phase 359.`
- Focused status test compiles and passes.
- YAML validation passes for the Phase 360 design/checklist artifacts.
- Static guard confirms the split stale aggregate guard for `range(168, 360)` and no unintended contiguous stale literal.
- S1 does not create `acceptance.md`.
- S1 does not modify prohibited files, stage, commit, push, or start Phase 361.
