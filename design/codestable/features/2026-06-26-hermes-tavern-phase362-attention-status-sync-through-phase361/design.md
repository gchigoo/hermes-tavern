---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase362-attention-status-sync-through-phase361
title: "Phase 362 attention/status sync through Phase 361"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 362 attention/status sync through accepted Phase 361."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase362]
---

# Phase 362 attention/status sync through Phase 361

## Background / Current Status

Phase 361 is accepted:

`design/codestable/features/2026-06-26-hermes-tavern-phase361-attention-status-sync-through-phase360/acceptance.md`

Inspected baseline:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-361 accepted`.
- Terminal suffix is `Phase 359 attention status sync through Phase 358, Phase 360 attention status sync through Phase 359, and Phase 361 attention status sync through Phase 360.`
- `tests/test_hermes_tavern_codestable_status.py` has `CURRENT_STATUS_PREFIX` pinned to Phase 361.
- The focused status test currently has stale prefix and markers for Phase 360.
- The focused status test currently uses `phase_range = range(168, 362)` and live aggregate string `range(168, 362)`.
- The focused status test already includes the split stale aggregate guard for `range(168, 361)`.

Range note: Phase 362 must advance the live range to `range(168, 363)` and add a split stale guard for `range(168, 362)`.

## Goals

- Controller materializes the Phase 362 design/checklist artifacts before executor S1.
- Advance `design/codestable/attention.md` exactly one status tick from 1-361 to 1-362.
- Append `Phase 362 attention status sync through Phase 361` exactly once.
- Update the focused status regression to guard the Phase 362 live status contract.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 362 label.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No root docs, architecture, roadmap, requirements, or compound updates.
- No service lifecycle commands, cache artifacts, staging, commits, or pushes.
- No `acceptance.md` creation during executor S1.
- No executor edits to design/checklist artifacts.
- No Phase 363 work.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No provider-safety, content, RP, or adult-fiction behavior changes.

## S1/S2 Boundary

Controller pre-S1 owns artifact materialization for:

- `design/codestable/features/2026-06-26-hermes-tavern-phase362-attention-status-sync-through-phase361/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase362-attention-status-sync-through-phase361/checklist.yaml`

Executor S1 may edit only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

Executor S1 must not create `acceptance.md`, edit design/checklist artifacts, stage, commit, push, touch Phase 363, or touch prohibited runtime/source/plugin/provider/gateway/CLI/config/dependency/root docs/architecture/roadmap/requirements/compound/build/service lifecycle/cache paths.

Controller S2 owns verification, `acceptance.md` creation, and final checklist status updates after verification. After verified S2 finalization, the parent cron controller may stage, commit, push, and verify remote/CI per the unattended job policy.

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-361 accepted` -> `All phases 1-362 accepted`
- Move `and` from Phase 361 to Phase 362.
- Append `Phase 362 attention status sync through Phase 361` after Phase 361.
- Final suffix must be `Phase 360 attention status sync through Phase 359, Phase 361 attention status sync through Phase 360, and Phase 362 attention status sync through Phase 361.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-361` -> `1-362`
- `STALE_STATUS_PREFIX`: `1-360` -> `1-361`
- `STALE_PHASE_MARKER`: `1-360` -> `1-361`
- `STALE_PHASE_MARKER_EN_DASH`: `1–360` -> `1–361`
- Add `"Phase 362 attention status sync through Phase 361"` to `REQUIRED_PHASE_LABELS`
- `FINAL_STATUS_SUFFIX`: `Phase 360 attention status sync through Phase 359, Phase 361 attention status sync through Phase 360, and Phase 362 attention status sync through Phase 361.`
- `phase_range`: `range(168, 362)` -> `range(168, 363)`
- Live `aggregate_range`: `"range(168, 362)"` -> `"range(168, 363)"`
- Add split stale guard `stale_aggregate_range_362 = "".join(["range(168, ", "36", "2", ")"])`
- Include `stale_aggregate_range_362` in the stale range assertion tuple.
- Do not leave a contiguous literal `range(168, 362)` in test source after S1; the stale guard must be split and the live aggregate must be `range(168, 363)`.

## Structure Health

This is docs/static-test/status-only. No source structure, module boundary, dependency graph, runtime flow, architecture, roadmap, requirement, compound document, service lifecycle, cache, staging, commit, or push changes are involved. No microrefactor is allowed or useful for this slice.

## Acceptance Contract For Controller S2

- `attention.md` has exactly one current status line.
- Current status line starts with `Current status (2026-06-18): All phases 1-362 accepted`.
- Current status line contains `Phase 362 attention status sync through Phase 361` exactly once.
- Current status line preserves `Phase 121-167` and every explicit Phase 168 through Phase 362 label.
- Current status line ends with `Phase 360 attention status sync through Phase 359, Phase 361 attention status sync through Phase 360, and Phase 362 attention status sync through Phase 361.`
- Focused status test compiles and passes.
- YAML validation passes for the Phase 362 design/checklist artifacts and S2 acceptance artifact.
- Static guard confirms the split stale aggregate guard for `range(168, 362)` and no contiguous stale literal in test source.
- Changed-path/protected-path guard confirms only controller/S1/S2 allowed Phase 362 status files changed.
- `git diff --check` passes.
- Cached whitespace check passes.
- Full `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider` runs when feasible.
- S1 does not create `acceptance.md`.
- S1 and S2 do not touch Phase 363 or modify prohibited files; executor S1 must not stage/commit/push, while the parent cron controller may stage/commit/push only after verified S2 finalization per policy.
