---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase366-attention-status-sync-through-phase365
title: "Phase 366 attention/status sync through Phase 365"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 366 attention/status sync through accepted Phase 365."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase366]
---

# Phase 366 attention/status sync through Phase 365

## Background / Current Status

Phase 365 is accepted:

`design/codestable/features/2026-06-26-hermes-tavern-phase365-attention-status-sync-through-phase364/acceptance.md`

Inspected baseline:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-365 accepted`.
- Terminal suffix is `Phase 363 attention status sync through Phase 362, Phase 364 attention status sync through Phase 363, and Phase 365 attention status sync through Phase 364.`
- `tests/test_hermes_tavern_codestable_status.py` has `CURRENT_STATUS_PREFIX` pinned to Phase 365.
- The focused status test currently has stale prefix and markers for Phase 364.
- The focused status test currently uses `phase_range = range(168, 366)` and live aggregate string `range(168, 366)`.
- The focused status test already includes the split stale aggregate guard for `range(168, 365)`.

Range note: Phase 366 must advance the live range to `range(168, 367)` and add a split stale guard for `range(168, 366)`.

## Goals

- Materialize the Phase 366 design/checklist artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-365 to 1-366.
- Append `Phase 366 attention status sync through Phase 365` exactly once.
- Update the focused status regression to guard the Phase 366 live status contract.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 366 label; do not drop Phase 365.
- Leave the checklist in non-final S1 handoff state for parent verification.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No root docs, architecture, roadmap, requirements, or compound updates.
- No service lifecycle commands, cache artifacts, staging, commits, or pushes.
- No `acceptance.md` creation during executor S1.
- No final accepted/completed/passed closeout during executor S1.
- No Phase 367 work.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No provider-safety, content, RP, adult-fiction behavior, or minor-related behavior changes.

## S1/S2 Boundary

Executor S1 may edit only exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase366-attention-status-sync-through-phase365/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase366-attention-status-sync-through-phase365/checklist.yaml`

Executor S1 must not create `acceptance.md`, stage, commit, push, touch Phase 367, or touch prohibited runtime/source/plugin/provider/gateway/CLI/config/dependency/root docs/architecture/roadmap/requirements/compound/build/service lifecycle/cache paths.

Executor S1 may leave checklist S1 step/check statuses as `completed` only for completed executor work, with top-level `status: implemented`, `workflow_status: pending_parent_verification`, and `acceptance_state: pending_parent_verification`.

Controller S2 owns verification, any future `acceptance.md` creation, and final checklist status updates after verification.

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-365 accepted` -> `All phases 1-366 accepted`
- Move `and` from Phase 365 to Phase 366.
- Append `Phase 366 attention status sync through Phase 365` after Phase 365.
- Final suffix must be `Phase 364 attention status sync through Phase 363, Phase 365 attention status sync through Phase 364, and Phase 366 attention status sync through Phase 365.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-365` -> `1-366`
- `STALE_STATUS_PREFIX`: `1-364` -> `1-365`
- `STALE_PHASE_MARKER`: `1-364` -> `1-365`
- `STALE_PHASE_MARKER_EN_DASH`: `1–364` -> `1–365`
- Add `"Phase 366 attention status sync through Phase 365"` to `REQUIRED_PHASE_LABELS`; preserve Phase 365.
- `FINAL_STATUS_SUFFIX`: `Phase 364 attention status sync through Phase 363, Phase 365 attention status sync through Phase 364, and Phase 366 attention status sync through Phase 365.`
- `phase_range`: `range(168, 366)` -> `range(168, 367)`
- Live `aggregate_range`: `"range(168, 366)"` -> `"range(168, 367)"`
- Add split stale aggregate guard `stale_aggregate_range_366 = "".join(["range(168, ", "36", "6", ")"])`
- Include `stale_aggregate_range_366` in the stale range assertion tuple.
- Do not leave a contiguous literal `range(168, 366)` in test source after S1; the stale guard must be split and the live aggregate must be `range(168, 367)`.
- Add or preserve anchored single-assignment guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.

## Static Guard Plan

- `attention.md` has exactly one current-status line.
- Current status line starts with `Current status (2026-06-18): All phases 1-366 accepted`.
- Direct stale status `All phases 1-365 accepted` is absent from the attention status line.
- Current status line contains every `REQUIRED_PHASE_LABELS` entry.
- Current status line contains `Phase 366 attention status sync through Phase 365` exactly once.
- Current status line preserves `Phase 121-167` and every explicit Phase 168 through Phase 366 label; do not drop Phase 365.
- Test source has exactly one anchored assignment for `CURRENT_STATUS_PREFIX`.
- Test source has exactly one anchored assignment for `FINAL_STATUS_SUFFIX`.
- Test source has live `phase_range = range(168, 367)`.
- Test source has live aggregate string `range(168, 367)`.
- Test source has split stale aggregate guard for `range(168, 366)`.
- Test source has no contiguous stale `range(168, 366)` literal after S1.
- Changed/untracked paths are limited to the four S1-allowed files.

## Structure Health

This is docs/static-test/status-only. No source structure, module boundary, dependency graph, runtime flow, architecture, roadmap, requirement, compound document, service lifecycle, cache, staging, commit, or push changes are involved. No microrefactor is allowed or useful for this slice.

## Acceptance Contract For Controller S2

- `attention.md` has exactly one current status line.
- Current status line starts with `Current status (2026-06-18): All phases 1-366 accepted`.
- Current status line contains `Phase 366 attention status sync through Phase 365` exactly once.
- Current status line preserves `Phase 121-167` and every explicit Phase 168 through Phase 366 label, including Phase 365.
- Current status line ends with `Phase 364 attention status sync through Phase 363, Phase 365 attention status sync through Phase 364, and Phase 366 attention status sync through Phase 365.`
- Focused status test compiles and passes.
- YAML/frontmatter validation passes for the Phase 366 design/checklist artifacts.
- Static guard confirms anchored assignment counts for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.
- Static guard confirms the split stale aggregate guard for `range(168, 366)` and no contiguous stale literal in test source.
- Changed-path/protected-path guard confirms only S1-allowed Phase 366 status files changed.
- `git diff --check` passes.
- Full `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` runs when feasible.
- S1 does not create `acceptance.md`.
- S1 does not touch Phase 367 or prohibited files.
