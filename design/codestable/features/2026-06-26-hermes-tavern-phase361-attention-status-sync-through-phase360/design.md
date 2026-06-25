---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase361-attention-status-sync-through-phase360
title: "Phase 361 attention/status sync through Phase 360"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 361 attention/status sync through accepted Phase 360."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase361]
---

# Phase 361 attention/status sync through Phase 360

## Background / Current Status

Phase 360 is accepted:

`design/codestable/features/2026-06-26-hermes-tavern-phase360-attention-status-sync-through-phase359/acceptance.md`

Controller-verified baseline:

- Repository status is clean.
- No Phase 361 feature directory exists.
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-360 accepted`.
- Terminal suffix is `Phase 358 attention status sync through Phase 357, Phase 359 attention status sync through Phase 358, and Phase 360 attention status sync through Phase 359.`
- `tests/test_hermes_tavern_codestable_status.py` has `CURRENT_STATUS_PREFIX` pinned to Phase 360.
- The focused status test currently has stale prefix and markers for Phase 359.
- The focused status test currently uses `phase_range = range(168, 361)` and live aggregate string `range(168, 361)`.
- The focused status test already includes the split stale aggregate guard for `range(168, 360)`.

Range note: Phase 361 must advance the live range to `range(168, 362)` and add a split stale guard for `range(168, 361)`.

## Goals

- Create the Phase 361 design/checklist artifacts as implementation-ready S1 handoff artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-360 to 1-361.
- Append `Phase 361 attention status sync through Phase 360` exactly once.
- Update the focused status regression to guard the Phase 361 live status contract.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 361 label.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No root docs, architecture, roadmap, requirements, or compound updates.
- No service lifecycle commands or dependency installation.
- No `acceptance.md` creation during executor S1.
- No executor staging, commits, or pushes.
- No Phase 362 work.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No provider-safety, content, RP, or adult-fiction behavior changes.

## S1/S2 Boundary

Executor S1 may edit only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase361-attention-status-sync-through-phase360/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase361-attention-status-sync-through-phase360/checklist.yaml`

Executor S1 must not create `acceptance.md`, stage, commit, push, touch Phase 362, or touch prohibited runtime/source/plugin/provider/gateway/CLI/config/dependency/root docs/architecture/roadmap/requirements/compound/build paths.

Controller S2 owns verification, `acceptance.md` creation, final checklist status updates, and any parent commit/push action after verification.

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-360 accepted` -> `All phases 1-361 accepted`
- Move `and` from Phase 360 to Phase 361.
- Append `Phase 361 attention status sync through Phase 360` after Phase 360.
- Final suffix must be `Phase 359 attention status sync through Phase 358, Phase 360 attention status sync through Phase 359, and Phase 361 attention status sync through Phase 360.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-360` -> `1-361`
- `STALE_STATUS_PREFIX`: `1-359` -> `1-360`
- `STALE_PHASE_MARKER`: `1-359` -> `1-360`
- `STALE_PHASE_MARKER_EN_DASH`: `1–359` -> `1–360`
- Add `"Phase 361 attention status sync through Phase 360"` to `REQUIRED_PHASE_LABELS`
- `FINAL_STATUS_SUFFIX`: `Phase 359 attention status sync through Phase 358, Phase 360 attention status sync through Phase 359, and Phase 361 attention status sync through Phase 360.`
- `phase_range`: `range(168, 361)` -> `range(168, 362)`
- Live `aggregate_range`: `"range(168, 361)"` -> `"range(168, 362)"`
- Add split stale guard `stale_aggregate_range_361 = "".join(["range(168, ", "36", "1", ")"])`
- Include `stale_aggregate_range_361` in the stale range assertion tuple.
- Do not leave a contiguous literal `range(168, 361)` in test source after S1; the stale guard must be split and the live aggregate must be `range(168, 362)`.

## Structure Health

This is docs/static-test/status-only. No source structure, module boundary, dependency graph, runtime flow, architecture, roadmap, requirement, or compound document changes are involved. No microrefactor is allowed or useful for this slice.

## Acceptance Contract For Controller S2

- `attention.md` has exactly one current status line.
- Current status line starts with `Current status (2026-06-18): All phases 1-361 accepted`.
- Current status line contains `Phase 361 attention status sync through Phase 360` exactly once.
- Current status line preserves `Phase 121-167` and every explicit Phase 168 through Phase 361 label.
- Current status line ends with `Phase 359 attention status sync through Phase 358, Phase 360 attention status sync through Phase 359, and Phase 361 attention status sync through Phase 360.`
- Focused status test compiles and passes.
- YAML validation passes for the Phase 361 design/checklist artifacts.
- Static guard confirms the split stale aggregate guard for `range(168, 361)` and no contiguous stale literal.
- S1 does not create `acceptance.md`.
- S1 does not modify prohibited files, stage, commit, push, or touch Phase 362.
