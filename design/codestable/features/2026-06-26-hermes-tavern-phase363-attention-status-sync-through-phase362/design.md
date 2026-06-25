---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase363-attention-status-sync-through-phase362
title: "Phase 363 attention/status sync through Phase 362"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 363 attention/status sync through accepted Phase 362."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase363]
---

# Phase 363 attention/status sync through Phase 362

## Background / Current Status

Phase 362 is accepted:

`design/codestable/features/2026-06-26-hermes-tavern-phase362-attention-status-sync-through-phase361/acceptance.md`

Inspected baseline:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-362 accepted`.
- Terminal suffix is `Phase 360 attention status sync through Phase 359, Phase 361 attention status sync through Phase 360, and Phase 362 attention status sync through Phase 361.`
- `tests/test_hermes_tavern_codestable_status.py` has `CURRENT_STATUS_PREFIX` pinned to Phase 362.
- The focused status test currently has stale prefix and markers for Phase 361.
- The focused status test currently uses `phase_range = range(168, 363)` and live aggregate string `range(168, 363)`.
- The focused status test already includes the split stale aggregate guard for `range(168, 362)`.

Range note: Phase 363 must advance the live range to `range(168, 364)` and add a split stale guard for `range(168, 363)`.

## Goals

- Controller materializes the Phase 363 design/checklist artifacts before executor S1.
- Advance `design/codestable/attention.md` exactly one status tick from 1-362 to 1-363.
- Append `Phase 363 attention status sync through Phase 362` exactly once.
- Update the focused status regression to guard the Phase 363 live status contract.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 363 label.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No root docs, architecture, roadmap, requirements, or compound updates.
- No service lifecycle commands, cache artifacts, staging, commits, or pushes.
- No `acceptance.md` creation during executor S1.
- No executor edits to design/checklist artifacts.
- No Phase 364 work.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No provider-safety, content, RP, or adult-fiction behavior changes.

## S1/S2 Boundary

Controller pre-S1 owns artifact materialization for:

- `design/codestable/features/2026-06-26-hermes-tavern-phase363-attention-status-sync-through-phase362/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase363-attention-status-sync-through-phase362/checklist.yaml`

Executor S1 may edit only exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

Executor S1 must not create `acceptance.md`, edit design/checklist artifacts, stage, commit, push, touch Phase 364, or touch prohibited runtime/source/plugin/provider/gateway/CLI/config/dependency/root docs/architecture/roadmap/requirements/compound/build/service lifecycle/cache paths.

Controller S2 owns verification, `acceptance.md` creation, and final checklist status updates after verification. After verified S2 finalization, the parent cron controller may stage, commit, push, and verify remote/CI per the unattended job policy.

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-362 accepted` -> `All phases 1-363 accepted`
- Move `and` from Phase 362 to Phase 363.
- Append `Phase 363 attention status sync through Phase 362` after Phase 362.
- Final suffix must be `Phase 361 attention status sync through Phase 360, Phase 362 attention status sync through Phase 361, and Phase 363 attention status sync through Phase 362.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-362` -> `1-363`
- `STALE_STATUS_PREFIX`: `1-361` -> `1-362`
- `STALE_PHASE_MARKER`: `1-361` -> `1-362`
- `STALE_PHASE_MARKER_EN_DASH`: `1–361` -> `1–362`
- Add `"Phase 363 attention status sync through Phase 362"` to `REQUIRED_PHASE_LABELS`
- `FINAL_STATUS_SUFFIX`: `Phase 361 attention status sync through Phase 360, Phase 362 attention status sync through Phase 361, and Phase 363 attention status sync through Phase 362.`
- `phase_range`: `range(168, 363)` -> `range(168, 364)`
- Live `aggregate_range`: `"range(168, 363)"` -> `"range(168, 364)"`
- Add split stale guard `stale_aggregate_range_363 = "".join(["range(168, ", "36", "3", ")"])`
- Include `stale_aggregate_range_363` in the stale range assertion tuple.
- Do not leave a contiguous literal `range(168, 363)` in test source after S1; the stale guard must be split and the live aggregate must be `range(168, 364)`.

## Structure Health

This is docs/static-test/status-only. No source structure, module boundary, dependency graph, runtime flow, architecture, roadmap, requirement, compound document, service lifecycle, cache, staging, commit, or push changes are involved. No microrefactor is allowed or useful for this slice.

## Acceptance Contract For Controller S2

- `attention.md` has exactly one current status line.
- Current status line starts with `Current status (2026-06-18): All phases 1-363 accepted`.
- Current status line contains `Phase 363 attention status sync through Phase 362` exactly once.
- Current status line preserves `Phase 121-167` and every explicit Phase 168 through Phase 363 label.
- Current status line ends with `Phase 361 attention status sync through Phase 360, Phase 362 attention status sync through Phase 361, and Phase 363 attention status sync through Phase 362.`
- Focused status test compiles and passes.
- YAML validation passes for the Phase 363 design/checklist artifacts and S2 acceptance artifact.
- Static guard confirms the split stale aggregate guard for `range(168, 363)` and no contiguous stale literal in test source.
- Changed-path/protected-path guard confirms only controller/S1/S2 allowed Phase 363 status files changed.
- `git diff --check` passes.
- Cached whitespace check passes.
- Full `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider` runs when feasible.
- S1 does not create `acceptance.md`.
- S1 and S2 do not touch Phase 364 or modify prohibited files; executor S1 must not stage/commit/push, while the parent cron controller may stage/commit/push only after verified S2 finalization per policy.
