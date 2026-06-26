---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase365-attention-status-sync-through-phase364
title: "Phase 365 attention/status sync through Phase 364"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 365 attention/status sync through accepted Phase 364."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase365]
---

# Phase 365 attention/status sync through Phase 364

## Background / Current Status

Phase 364 is accepted:

`design/codestable/features/2026-06-26-hermes-tavern-phase364-attention-status-sync-through-phase363/acceptance.md`

Inspected baseline:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-364 accepted`.
- Terminal suffix is `Phase 362 attention status sync through Phase 361, Phase 363 attention status sync through Phase 362, and Phase 364 attention status sync through Phase 363.`
- `tests/test_hermes_tavern_codestable_status.py` has `CURRENT_STATUS_PREFIX` pinned to Phase 364.
- The focused status test currently has stale prefix and markers for Phase 363.
- The focused status test currently uses `phase_range = range(168, 365)` and live aggregate string `range(168, 365)`.
- The focused status test already includes the split stale aggregate guard for `range(168, 364)`.

Range note: Phase 365 must advance the live range to `range(168, 366)` and add a split stale guard for `range(168, 365)`.

## Goals

- Materialize the Phase 365 design/checklist artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-364 to 1-365.
- Append `Phase 365 attention status sync through Phase 364` exactly once.
- Update the focused status regression to guard the Phase 365 live status contract.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 365 label.
- Leave the checklist in non-final S1 handoff state for parent verification.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No root docs, architecture, roadmap, requirements, or compound updates.
- No service lifecycle commands, cache artifacts, staging, commits, or pushes.
- No `acceptance.md` creation during executor S1.
- No final accepted/completed/passed closeout during executor S1.
- No Phase 366 work.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No provider-safety, content, RP, adult-fiction behavior, or minor-related behavior changes.

## S1/S2 Boundary

Executor S1 may edit only exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase365-attention-status-sync-through-phase364/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase365-attention-status-sync-through-phase364/checklist.yaml`

Executor S1 must not create `acceptance.md`, stage, commit, push, touch Phase 366, or touch prohibited runtime/source/plugin/provider/gateway/CLI/config/dependency/root docs/architecture/roadmap/requirements/compound/build/service lifecycle/cache paths.

Executor S1 may leave checklist S1 step/check statuses as `completed` only for completed executor work, with top-level `status: implemented`, `workflow_status: pending_parent_verification`, and `acceptance_state: pending_parent_verification`.

Controller S2 owns verification, any future `acceptance.md` creation, and final checklist status updates after verification.

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-364 accepted` -> `All phases 1-365 accepted`
- Move `and` from Phase 364 to Phase 365.
- Append `Phase 365 attention status sync through Phase 364` after Phase 364.
- Final suffix must be `Phase 363 attention status sync through Phase 362, Phase 364 attention status sync through Phase 363, and Phase 365 attention status sync through Phase 364.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-364` -> `1-365`
- `STALE_STATUS_PREFIX`: `1-363` -> `1-364`
- `STALE_PHASE_MARKER`: `1-363` -> `1-364`
- `STALE_PHASE_MARKER_EN_DASH`: `1–363` -> `1–364`
- Add `"Phase 365 attention status sync through Phase 364"` to `REQUIRED_PHASE_LABELS`
- `FINAL_STATUS_SUFFIX`: `Phase 363 attention status sync through Phase 362, Phase 364 attention status sync through Phase 363, and Phase 365 attention status sync through Phase 364.`
- `phase_range`: `range(168, 365)` -> `range(168, 366)`
- Live `aggregate_range`: `"range(168, 365)"` -> `"range(168, 366)"`
- Add split stale aggregate guard `stale_aggregate_range_365 = "".join(["range(168, ", "36", "5", ")"])`
- Include `stale_aggregate_range_365` in the stale range assertion tuple.
- Do not leave a contiguous literal `range(168, 365)` in test source after S1; the stale guard must be split and the live aggregate must be `range(168, 366)`.
- Preserve existing anchored single-assignment guards and no-discovery-token guards.

## Structure Health

This is docs/static-test/status-only. No source structure, module boundary, dependency graph, runtime flow, architecture, roadmap, requirement, compound document, service lifecycle, cache, staging, commit, or push changes are involved. No microrefactor is allowed or useful for this slice.

## Acceptance Contract For Controller S2

- `attention.md` has exactly one current status line.
- Current status line starts with `Current status (2026-06-18): All phases 1-365 accepted`.
- Current status line contains `Phase 365 attention status sync through Phase 364` exactly once.
- Current status line preserves `Phase 121-167` and every explicit Phase 168 through Phase 365 label.
- Current status line ends with `Phase 363 attention status sync through Phase 362, Phase 364 attention status sync through Phase 363, and Phase 365 attention status sync through Phase 364.`
- Focused status test compiles and passes.
- YAML/frontmatter validation passes for the Phase 365 design/checklist artifacts.
- Static guard confirms the split stale aggregate guard for `range(168, 365)` and no contiguous stale literal in test source.
- Changed-path/protected-path guard confirms only S1-allowed Phase 365 status files changed.
- `git diff --check` passes.
- Full `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` runs when feasible.
- S1 does not create `acceptance.md`.
- S1 does not touch Phase 366 or prohibited files.
