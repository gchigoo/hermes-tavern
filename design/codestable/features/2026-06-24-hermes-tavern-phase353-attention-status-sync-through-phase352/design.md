---
doc_type: feature-design
feature: 2026-06-24-hermes-tavern-phase353-attention-status-sync-through-phase352
status: approved
implementation_ready: true
date: "2026-06-24"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 353 attention/status sync through accepted Phase 352."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase353]
---

# Phase 353: Attention Status Sync Through Phase 352

## Background / Current Status

Phase 352 is accepted:

`design/codestable/features/2026-06-24-hermes-tavern-phase352-attention-status-sync-through-phase351/acceptance.md`

Current live contract before Phase 353:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-352 accepted`.
- Terminal suffix is `Phase 350 attention status sync through Phase 349, Phase 351 attention status sync through Phase 350, and Phase 352 attention status sync through Phase 351.`
- The focused status test in this repo is `tests/test_hermes_tavern_codestable_status.py`.
- No Phase 353 feature directory exists.

Range note: after Phase 352 the live aggregate range is `range(168, 353)`. Phase 353 must advance the live range to `range(168, 354)` and add a split stale guard for `range(168, 353)`.

## Goals

- Create the Phase 353 design/checklist artifacts as implementation-ready S1 parent-handoff artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-352 to 1-353.
- Append `Phase 353 attention status sync through Phase 352` exactly once.
- Update the focused status regression to guard the Phase 353 live status contract.
- Preserve every historical label exactly, including `Phase 121-167` and explicit Phase 168 through Phase 353 labels.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No architecture, roadmap, requirements, compound, root README, or root design updates.
- No service lifecycle commands or dependency installation.
- No acceptance.md creation.
- No commits, staging, or pushes.
- No Phase 354 work.

## Exact Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-24-hermes-tavern-phase353-attention-status-sync-through-phase352/design.md`
- `design/codestable/features/2026-06-24-hermes-tavern-phase353-attention-status-sync-through-phase352/checklist.yaml`

Prohibited:
- `acceptance.md` (not for S1 non-final handoff)
- Runtime Python files, plugin source, provider/gateway code, CLI, config
- Architecture, roadmap, requirements, compound documents
- Root README, root design, build scripts
- Service lifecycle commands, dependency installation
- Commits, staging, pushes
- Phase 354 work or directory

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-352 accepted` -> `All phases 1-353 accepted`
- Move `and` from Phase 352 (was final) to Phase 353 (new final)
- Append `Phase 353 attention status sync through Phase 352` after Phase 352, with `and` only on Phase 353
- Final suffix must be `Phase 351 attention status sync through Phase 350, Phase 352 attention status sync through Phase 351, and Phase 353 attention status sync through Phase 352.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-352` -> `1-353`
- `STALE_STATUS_PREFIX`: `1-351` -> `1-352`
- `STALE_PHASE_MARKER`: `1-351` -> `1-352`
- `STALE_PHASE_MARKER_EN_DASH`: `1–351` -> `1–352`
- Add `"Phase 353 attention status sync through Phase 352"` to REQUIRED_PHASE_LABELS
- `FINAL_STATUS_SUFFIX`: `Phase 351 attention status sync through Phase 350, Phase 352 attention status sync through Phase 351, and Phase 353 attention status sync through Phase 352.`
- `phase_range`: `range(168, 353)` -> `range(168, 354)`
- `aggregate_range`: `"range(168, 353)"` -> `"range(168, 354)"`
- New split stale guard `stale_aggregate_range_353` = `"".join(["range(168, ", "35", "3", ")"])`
- Add the new stale guard to the stale range assertion tuple
- Do not leave a contiguous `range(168, 353)` literal in the test source

## Acceptance Contract For Controller S2

- `attention.md` has exactly one current status line.
- Current status line starts with `Current status (2026-06-18): All phases 1-353 accepted`.
- Current status line contains `Phase 353 attention status sync through Phase 352` exactly once.
- Current status line preserves `Phase 121-167` and every explicit Phase 168 through Phase 353 label.
- Current status line ends with `Phase 351 attention status sync through Phase 350, Phase 352 attention status sync through Phase 351, and Phase 353 attention status sync through Phase 352.`
- Focused test compiles and passes.
- YAML validation passes for the Phase 353 design/checklist artifacts.
- Static guard confirms no contiguous stale `range(168, 353)` literal remains in `tests/test_hermes_tavern_codestable_status.py`.
- S1 does not create `acceptance.md`; acceptance remains controller-only.
