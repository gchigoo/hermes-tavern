---
doc_type: feature-design
feature: 2026-06-25-hermes-tavern-phase356-attention-status-sync-through-phase355
status: approved
implementation_ready: true
date: "2026-06-25"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 356 attention/status sync through accepted Phase 355."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase356]
---

# Phase 356: Attention Status Sync Through Phase 355

## Background / Current Status

Phase 355 is accepted:

`design/codestable/features/2026-06-25-hermes-tavern-phase355-attention-status-sync-through-phase354/acceptance.md`

Current live contract before Phase 356:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-355 accepted`.
- Terminal suffix is `Phase 353 attention status sync through Phase 352, Phase 354 attention status sync through Phase 353, and Phase 355 attention status sync through Phase 354.`
- The focused status test is `tests/test_hermes_tavern_codestable_status.py`.
- The focused status test currently pins Phase 355 with `phase_range = range(168, 356)` and live aggregate string `range(168, 356)`.
- No Phase 356 feature directory exists.

Range note: after Phase 355 the live aggregate range is `range(168, 356)`. Phase 356 must advance the live range to `range(168, 357)` and add a split stale guard for `range(168, 356)`.

## Goals

- Create the Phase 356 design/checklist artifacts as implementation-ready S1 parent-handoff artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-355 to 1-356.
- Append `Phase 356 attention status sync through Phase 355` exactly once.
- Update the focused status regression to guard the Phase 356 live status contract.
- Preserve every historical label exactly, including `Phase 121-167` and explicit Phase 168 through Phase 356 labels.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No root docs, architecture, roadmap, requirements, or compound updates.
- No service lifecycle commands or dependency installation.
- No acceptance.md creation during executor S1; controller S2 owns any acceptance report.
- No executor commits, staging, or pushes; parent controller owns final commit/push after verification.
- No Phase 357 work.

## Exact Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-25-hermes-tavern-phase356-attention-status-sync-through-phase355/design.md`
- `design/codestable/features/2026-06-25-hermes-tavern-phase356-attention-status-sync-through-phase355/checklist.yaml`

Prohibited:
- `acceptance.md` during executor S1
- Runtime Python files, plugin source, provider/gateway code, CLI, config
- Dependency, build, service lifecycle, or cache-artifact changes
- Root docs, architecture, roadmap, requirements, or compound documents
- Commits, staging, pushes
- Phase 357 work or directory

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-355 accepted` -> `All phases 1-356 accepted`
- Move `and` from Phase 355 (was final) to Phase 356 (new final)
- Append `Phase 356 attention status sync through Phase 355` after Phase 355, with `and` only on Phase 356
- Final suffix must be `Phase 354 attention status sync through Phase 353, Phase 355 attention status sync through Phase 354, and Phase 356 attention status sync through Phase 355.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-355` -> `1-356`
- `STALE_STATUS_PREFIX`: `1-354` -> `1-355`
- `STALE_PHASE_MARKER`: `1-354` -> `1-355`
- `STALE_PHASE_MARKER_EN_DASH`: `1–354` -> `1–355`
- Add `"Phase 356 attention status sync through Phase 355"` to `REQUIRED_PHASE_LABELS`
- `FINAL_STATUS_SUFFIX`: `Phase 354 attention status sync through Phase 353, Phase 355 attention status sync through Phase 354, and Phase 356 attention status sync through Phase 355.`
- `phase_range`: `range(168, 356)` -> `range(168, 357)`
- Every live `aggregate_range`: `"range(168, 356)"` -> `"range(168, 357)"`
- New split stale guard `stale_aggregate_range_356` = `"".join(["range(168, ", "35", "6", ")"])`
- Add the new stale guard to the stale range assertion tuple
- Do not leave a contiguous `range(168, 356)` literal in the test source

## Acceptance Contract For Controller S2

- `attention.md` has exactly one current status line.
- Current status line starts with `Current status (2026-06-18): All phases 1-356 accepted`.
- Current status line contains `Phase 356 attention status sync through Phase 355` exactly once.
- Current status line preserves `Phase 121-167` and every explicit Phase 168 through Phase 356 label.
- Current status line ends with `Phase 354 attention status sync through Phase 353, Phase 355 attention status sync through Phase 354, and Phase 356 attention status sync through Phase 355.`
- Focused test compiles and passes.
- YAML validation passes for the Phase 356 design/checklist artifacts.
- Static guard confirms no contiguous stale `range(168, 356)` literal remains in `tests/test_hermes_tavern_codestable_status.py`.
- S1 does not create `acceptance.md`; acceptance remains controller-only.
