---
doc_type: feature-design
feature: 2026-06-25-hermes-tavern-phase358-attention-status-sync-through-phase357
status: approved
implementation_ready: true
date: "2026-06-25"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 358 attention/status sync through accepted Phase 357."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase358]
---

# Phase 358: Attention Status Sync Through Phase 357

## Background / Current Status

Phase 357 is accepted:

`design/codestable/features/2026-06-25-hermes-tavern-phase357-attention-status-sync-through-phase356/acceptance.md`

Controller-verified baseline:

- Git branch `main` is clean at `c385dec`.
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-357 accepted`.
- Terminal suffix is `Phase 355 attention status sync through Phase 354, Phase 356 attention status sync through Phase 355, and Phase 357 attention status sync through Phase 356.`
- The focused status test is `tests/test_hermes_tavern_codestable_status.py`.
- The focused status test currently pins Phase 357 with `phase_range = range(168, 358)` and live aggregate string `range(168, 358)`.
- The focused status test already includes the split stale guard for `range(168, 357)`.
- No Phase 358 feature directory exists.

Range note: after Phase 357 the live aggregate range is `range(168, 358)`. Phase 358 must advance the live range to `range(168, 359)` and add a split stale guard for `range(168, 358)`.

## Goals

- Create the Phase 358 design/checklist artifacts as implementation-ready S1 parent-handoff artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-357 to 1-358.
- Append `Phase 358 attention status sync through Phase 357` exactly once.
- Update the focused status regression to guard the Phase 358 live status contract.
- Preserve every historical label exactly, including `Phase 121-167` and explicit Phase 168 through Phase 358 labels.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No root docs, architecture, roadmap, requirements, or compound updates.
- No service lifecycle commands or dependency installation.
- No acceptance.md creation during executor S1; controller S2 owns any acceptance report after verification.
- No executor commits, staging, or pushes; parent controller owns final commit/push after verification if policy allows.
- No Phase 359 work.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No content, RP, provider-safety, or adult-fiction behavior changes; existing boundaries remain unchanged.

## Exact Allowed Files

Executor S1 allowed files are exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-25-hermes-tavern-phase358-attention-status-sync-through-phase357/design.md`
- `design/codestable/features/2026-06-25-hermes-tavern-phase358-attention-status-sync-through-phase357/checklist.yaml`

Prohibited:

- `acceptance.md` during executor S1
- Runtime Python files, plugin source, provider/gateway code, CLI, config
- Dependency, build, service lifecycle, or cache-artifact changes
- Root docs, architecture, roadmap, requirements, or compound documents
- Commits, staging, pushes
- Phase 359 work or directory

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-357 accepted` -> `All phases 1-358 accepted`
- Move `and` from Phase 357 (was final) to Phase 358 (new final)
- Append `Phase 358 attention status sync through Phase 357` after Phase 357, with `and` only on Phase 358
- Final suffix must be `Phase 356 attention status sync through Phase 355, Phase 357 attention status sync through Phase 356, and Phase 358 attention status sync through Phase 357.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-357` -> `1-358`
- `STALE_STATUS_PREFIX`: `1-356` -> `1-357`
- `STALE_PHASE_MARKER`: `1-356` -> `1-357`
- `STALE_PHASE_MARKER_EN_DASH`: `1–356` -> `1–357`
- Add `"Phase 358 attention status sync through Phase 357"` to `REQUIRED_PHASE_LABELS`
- `FINAL_STATUS_SUFFIX`: `Phase 356 attention status sync through Phase 355, Phase 357 attention status sync through Phase 356, and Phase 358 attention status sync through Phase 357.`
- `phase_range`: `range(168, 358)` -> `range(168, 359)`
- Every live `aggregate_range`: `"range(168, 358)"` -> `"range(168, 359)"`
- New split stale guard `stale_aggregate_range_358` = `"".join(["range(168, ", "35", "8", ")"])`
- Add `stale_aggregate_range_358` to the stale range assertion tuple
- Do not leave a contiguous `range(168, 358)` literal in the test source except as the split stale guard

## Acceptance Contract For Controller S2

- `attention.md` has exactly one current status line.
- Current status line starts with `Current status (2026-06-18): All phases 1-358 accepted`.
- Current status line contains `Phase 358 attention status sync through Phase 357` exactly once.
- Current status line preserves `Phase 121-167` and every explicit Phase 168 through Phase 358 label.
- Current status line ends with `Phase 356 attention status sync through Phase 355, Phase 357 attention status sync through Phase 356, and Phase 358 attention status sync through Phase 357.`
- Focused test compiles and passes.
- YAML validation passes for the Phase 358 design/checklist artifacts.
- Static guard confirms no contiguous stale `range(168, 358)` literal remains in `tests/test_hermes_tavern_codestable_status.py`.
- S1 does not create `acceptance.md`; acceptance remains controller-only.
- S1 does not modify prohibited files, commit, stage, push, or start Phase 359.
