---
doc_type: feature-design
feature: 2026-06-25-hermes-tavern-phase355-attention-status-sync-through-phase354
status: approved
implementation_ready: true
date: "2026-06-25"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 355 attention/status sync through accepted Phase 354."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase355]
---

# Phase 355: Attention Status Sync Through Phase 354

## Background / Current Status

Phase 354 is accepted:

`design/codestable/features/2026-06-24-hermes-tavern-phase354-attention-status-sync-through-phase353/acceptance.md`

Current live contract before Phase 355:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-354 accepted`.
- Terminal suffix is `Phase 352 attention status sync through Phase 351, Phase 353 attention status sync through Phase 352, and Phase 354 attention status sync through Phase 353.`
- The focused status test is `tests/test_hermes_tavern_codestable_status.py`.
- The focused status test currently pins Phase 354 with `phase_range = range(168, 355)` and live aggregate string `range(168, 355)`.
- No Phase 355 feature directory exists.

Range note: after Phase 354 the live aggregate range is `range(168, 355)`. Phase 355 must advance the live range to `range(168, 356)` and add a split stale guard for `range(168, 355)`.

## Goals

- Create the Phase 355 design/checklist artifacts as implementation-ready S1 parent-handoff artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-354 to 1-355.
- Append `Phase 355 attention status sync through Phase 354` exactly once.
- Update the focused status regression to guard the Phase 355 live status contract.
- Preserve every historical label exactly, including `Phase 121-167` and explicit Phase 168 through Phase 355 labels.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No root docs, architecture, roadmap, requirements, or compound updates.
- No service lifecycle commands or dependency installation.
- No acceptance.md creation during executor S1; controller S2 owns any acceptance report.
- No executor commits, staging, or pushes; parent controller owns final commit/push after verification.
- No Phase 356 work.

## Exact Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-25-hermes-tavern-phase355-attention-status-sync-through-phase354/design.md`
- `design/codestable/features/2026-06-25-hermes-tavern-phase355-attention-status-sync-through-phase354/checklist.yaml`

Prohibited:
- `acceptance.md` during executor S1
- Runtime Python files, plugin source, provider/gateway code, CLI, config
- Dependency, build, service lifecycle, or cache-artifact changes
- Root docs, architecture, roadmap, requirements, or compound documents
- Commits, staging, pushes
- Phase 356 work or directory

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-354 accepted` -> `All phases 1-355 accepted`
- Move `and` from Phase 354 (was final) to Phase 355 (new final)
- Append `Phase 355 attention status sync through Phase 354` after Phase 354, with `and` only on Phase 355
- Final suffix must be `Phase 353 attention status sync through Phase 352, Phase 354 attention status sync through Phase 353, and Phase 355 attention status sync through Phase 354.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-354` -> `1-355`
- `STALE_STATUS_PREFIX`: `1-353` -> `1-354`
- `STALE_PHASE_MARKER`: `1-353` -> `1-354`
- `STALE_PHASE_MARKER_EN_DASH`: `1–353` -> `1–354`
- Add `"Phase 355 attention status sync through Phase 354"` to `REQUIRED_PHASE_LABELS`
- `FINAL_STATUS_SUFFIX`: `Phase 353 attention status sync through Phase 352, Phase 354 attention status sync through Phase 353, and Phase 355 attention status sync through Phase 354.`
- `phase_range`: `range(168, 355)` -> `range(168, 356)`
- Every live `aggregate_range`: `"range(168, 355)"` -> `"range(168, 356)"`
- New split stale guard `stale_aggregate_range_355` = `"".join(["range(168, ", "35", "5", ")"])`
- Add the new stale guard to the stale range assertion tuple
- Do not leave a contiguous `range(168, 355)` literal in the test source

## Acceptance Contract For Controller S2

- `attention.md` has exactly one current status line.
- Current status line starts with `Current status (2026-06-18): All phases 1-355 accepted`.
- Current status line contains `Phase 355 attention status sync through Phase 354` exactly once.
- Current status line preserves `Phase 121-167` and every explicit Phase 168 through Phase 355 label.
- Current status line ends with `Phase 353 attention status sync through Phase 352, Phase 354 attention status sync through Phase 353, and Phase 355 attention status sync through Phase 354.`
- Focused test compiles and passes.
- YAML validation passes for the Phase 355 design/checklist artifacts.
- Static guard confirms no contiguous stale `range(168, 355)` literal remains in `tests/test_hermes_tavern_codestable_status.py`.
- S1 does not create `acceptance.md`; acceptance remains controller-only.
