---
doc_type: feature-design
feature: 2026-06-24-hermes-tavern-phase352-attention-status-sync-through-phase351
status: approved
implementation_ready: true
date: "2026-06-24"
owner: company_boost_lane
lane: company-boost
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 352 attention/status sync through accepted Phase 351."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase352]
---

# Phase 352: Attention Status Sync Through Phase 351

## Background / Current Status

Phase 351 is accepted:

`design/codestable/features/2026-06-24-hermes-tavern-phase351-attention-status-sync-through-phase350/acceptance.md`

Current live contract before Phase 352:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-351 accepted`.
- Terminal suffix is `Phase 349 attention status sync through Phase 348, Phase 350 attention status sync through Phase 349, and Phase 351 attention status sync through Phase 350.`
- The focused status test in this repo is `tests/test_hermes_tavern_codestable_status.py`.
- No Phase 352 feature directory exists.

Range note: after Phase 351 the live aggregate range is already `range(168, 352)`. Phase 352 must advance the live range to `range(168, 353)` and add a split stale guard for `range(168, 352)`.

## Goals

- Create the Phase 352 design/checklist artifacts as implementation-ready S1 parent-handoff artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-351 to 1-352.
- Append `Phase 352 attention status sync through Phase 351` exactly once.
- Update the focused status regression to guard the Phase 352 live status contract.
- Preserve every historical label exactly, including `Phase 121-167` and explicit Phase 168 through Phase 352 labels.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No architecture, roadmap, requirements, compound, root README, or root design updates.
- No service lifecycle commands or dependency installation.
- No acceptance.md creation.
- No commits, staging, or pushes.
- No Phase 353 work.

## Exact Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-24-hermes-tavern-phase352-attention-status-sync-through-phase351/design.md`
- `design/codestable/features/2026-06-24-hermes-tavern-phase352-attention-status-sync-through-phase351/checklist.yaml`

Prohibited:
- `acceptance.md` (not for S1 non-final handoff)
- Runtime Python files, plugin source, provider/gateway code, CLI, config
- Architecture, roadmap, requirements, compound documents
- Root README, root design, build scripts
- Service lifecycle commands, dependency installation
- Commits, staging, pushes
- Phase 353 work or directory

## Expected S1 Mechanical Changes

### attention.md

- Line 47: `All phases 1-351 accepted` → `All phases 1-352 accepted`
- Move `and` from Phase 351 (was final) to Phase 352 (new final)
- Append `Phase 352 attention status sync through Phase 351` after Phase 351, with `and` only on Phase 352

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-351` → `1-352`
- `STALE_STATUS_PREFIX`: `1-350` → `1-351`
- `STALE_PHASE_MARKER`: `1-350` → `1-351`
- `STALE_PHASE_MARKER_EN_DASH`: `1–350` → `1–351`
- Add `"Phase 352 attention status sync through Phase 351"` to REQUIRED_PHASE_LABELS
- `FINAL_STATUS_SUFFIX`: `Phase 350 attention status sync through Phase 349, Phase 351 attention status sync through Phase 350, and Phase 352 attention status sync through Phase 351.`
- `phase_range`: `range(168, 352)` → `range(168, 353)`
- `aggregate_range`: `"range(168, 352)"` → `"range(168, 353)"`
- New split stale guard `stale_aggregate_range_352` = `"".join(["range(168, ", "35", "2", ")"])`
- Add to stale_range assertion list and tuple
