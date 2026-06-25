---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase359-attention-status-sync-through-phase358
status: approved
implementation_ready: true
date: "2026-06-26"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 359 attention/status sync through accepted Phase 358."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase359]
---

# Phase 359: Attention Status Sync Through Phase 358

## Background / Current Status

Phase 358 is accepted:

`design/codestable/features/2026-06-25-hermes-tavern-phase358-attention-status-sync-through-phase357/acceptance.md`

Controller-verified baseline:

- Git branch `main` is clean at `c57833f`.
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-358 accepted`.
- Terminal suffix is `Phase 356 attention status sync through Phase 355, Phase 357 attention status sync through Phase 356, and Phase 358 attention status sync through Phase 357.`
- The focused status test is `tests/test_hermes_tavern_codestable_status.py`.
- The focused status test currently pins Phase 358 with `phase_range = range(168, 359)` and live aggregate string `range(168, 359)`.
- The focused status test already includes the split stale guard for `range(168, 358)`.
- No Phase 359 feature directory exists.

Range note: after Phase 358 the live aggregate range is `range(168, 359)`. Phase 359 must advance the live range to `range(168, 360)` and add a split stale guard for `range(168, 359)`.

## Goals

- Create the Phase 359 design/checklist artifacts as implementation-ready S1 parent-handoff artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-358 to 1-359.
- Append `Phase 359 attention status sync through Phase 358` exactly once.
- Update the focused status regression to guard the Phase 359 live status contract.
- Preserve every historical label exactly, including `Phase 121-167` and explicit Phase 168 through Phase 359 labels.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No root docs, architecture, roadmap, requirements, or compound updates.
- No service lifecycle commands or dependency installation.
- No acceptance.md creation during executor S1; controller S2 owns any acceptance report after verification.
- No executor commits, staging, or pushes; parent controller owns final commit/push after verification if policy allows.
- No Phase 360 work.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No content, RP, provider-safety, or adult-fiction behavior changes; existing boundaries remain unchanged.

## Exact Allowed Files

Executor S1 allowed files are exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase359-attention-status-sync-through-phase358/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase359-attention-status-sync-through-phase358/checklist.yaml`

Prohibited:

- `acceptance.md` during executor S1
- Runtime Python files, plugin source, provider/gateway code, CLI, config
- Dependency, build, service lifecycle, or cache-artifact changes
- Root docs, architecture, roadmap, requirements, or compound documents
- Commits, staging, pushes
- Phase 360 work or directory

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-358 accepted` -> `All phases 1-359 accepted`
- Move `and` from Phase 358 (was final) to Phase 359 (new final)
- Append `Phase 359 attention status sync through Phase 358` after Phase 358, with `and` only on Phase 359
- Final suffix must be `Phase 357 attention status sync through Phase 356, Phase 358 attention status sync through Phase 357, and Phase 359 attention status sync through Phase 358.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-358` -> `1-359`
- `STALE_STATUS_PREFIX`: `1-357` -> `1-358`
- `STALE_PHASE_MARKER`: `1-357` -> `1-358`
- `STALE_PHASE_MARKER_EN_DASH`: `1–357` -> `1–358`
- Add `"Phase 359 attention status sync through Phase 358"` to `REQUIRED_PHASE_LABELS`
- `FINAL_STATUS_SUFFIX`: `Phase 357 attention status sync through Phase 356, Phase 358 attention status sync through Phase 357, and Phase 359 attention status sync through Phase 358.`
- `phase_range`: `range(168, 359)` -> `range(168, 360)`
- Every live `aggregate_range`: `"range(168, 359)"` -> `"range(168, 360)"`
- New split stale guard `stale_aggregate_range_359` = `"".join(["range(168, ", "35", "9", ")"])`
- Add `stale_aggregate_range_359` to the stale range assertion tuple
- Do not leave a contiguous `range(168, 359)` literal in the test source; the stale guard must be split

## Acceptance Contract For Controller S2

- `attention.md` has exactly one current status line.
- Current status line starts with `Current status (2026-06-18): All phases 1-359 accepted`.
- Current status line contains `Phase 359 attention status sync through Phase 358` exactly once.
- Current status line preserves `Phase 121-167` and every explicit Phase 168 through Phase 359 label.
- Current status line ends with `Phase 357 attention status sync through Phase 356, Phase 358 attention status sync through Phase 357, and Phase 359 attention status sync through Phase 358.`
- Focused test compiles and passes.
- YAML validation passes for the Phase 359 design/checklist artifacts.
- Static guard confirms no contiguous stale `range(168, 359)` literal remains in `tests/test_hermes_tavern_codestable_status.py`.
- S1 does not create `acceptance.md`; acceptance remains controller-only.
- S1 does not modify prohibited files, commit, stage, push, or start Phase 360.
