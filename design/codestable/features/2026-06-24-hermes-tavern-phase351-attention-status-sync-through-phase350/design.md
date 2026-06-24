---
doc_type: feature-design
feature: 2026-06-24-hermes-tavern-phase351-attention-status-sync-through-phase350
status: approved
implementation_ready: true
date: "2026-06-24"
owner: company_boost_lane
lane: company-boost
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 351 attention/status sync through accepted Phase 350."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase351]
---

# Phase 351: Attention Status Sync Through Phase 350

## Background / Current Status

Phase 350 is accepted:

`design/codestable/features/2026-06-24-hermes-tavern-phase350-attention-status-sync-through-phase349/acceptance.md`

Current live contract before Phase 351:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-350 accepted`.
- Terminal suffix is `Phase 348 attention status sync through Phase 347, Phase 349 attention status sync through Phase 348, and Phase 350 attention status sync through Phase 349.`
- The focused status test in this repo is `tests/test_hermes_tavern_codestable_status.py`.
- No Phase 351 feature directory exists.

Path note: the request mentioned `tests/plugins/test_hermes_tavern_codestable_status.py`, but Phases 343-350 and the current repo use `tests/test_hermes_tavern_codestable_status.py`. Do not create a duplicate under `tests/plugins/`.

Range note: after Phase 350 the live aggregate range is already `range(168, 351)`. Phase 351 must advance the live range to `range(168, 352)` and add a split stale guard for `range(168, 351)`.

## Goals

- Create the Phase 351 design/checklist artifacts as implementation-ready S1 parent-handoff artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-350 to 1-351.
- Append `Phase 351 attention status sync through Phase 350` exactly once.
- Update the focused status regression to guard the Phase 351 live status contract.
- Preserve every historical label exactly, including `Phase 121-167` and explicit Phase 168 through Phase 351 labels.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No architecture, roadmap, requirements, compound, root README, or root design updates.
- No service lifecycle commands or dependency installation.
- No acceptance.md creation.
- No commits, staging, or pushes.
- No Phase 352 work.

## Exact Allowed Files

Executor may touch exactly these files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-24-hermes-tavern-phase351-attention-status-sync-through-phase350/design.md`
- `design/codestable/features/2026-06-24-hermes-tavern-phase351-attention-status-sync-through-phase350/checklist.yaml`

## Exact Status Line Change

Update the single current status line in `design/codestable/attention.md`:

- from prefix `Current status (2026-06-18): All phases 1-350 accepted`
- to prefix `Current status (2026-06-18): All phases 1-351 accepted`

Preserve all existing labels exactly, append `Phase 351 attention status sync through Phase 350` exactly once, and replace the terminal suffix:

- from `Phase 348 attention status sync through Phase 347, Phase 349 attention status sync through Phase 348, and Phase 350 attention status sync through Phase 349.`
- to `Phase 349 attention status sync through Phase 348, Phase 350 attention status sync through Phase 349, and Phase 351 attention status sync through Phase 350.`

## Test Contract Changes

Update `tests/test_hermes_tavern_codestable_status.py`:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-351 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-350 accepted"`
- `STALE_PHASE_MARKER = "1-350"`
- `STALE_PHASE_MARKER_EN_DASH = "1–350"`
- Add `"Phase 351 attention status sync through Phase 350"` to `REQUIRED_PHASE_LABELS` exactly once, after Phase 350.
- `FINAL_STATUS_SUFFIX = "Phase 349 attention status sync through Phase 348, Phase 350 attention status sync through Phase 349, and Phase 351 attention status sync through Phase 350."`
- `phase_range = range(168, 352)`
- `aggregate_range = "range(168, 352)"`
- Add split stale aggregate guard without leaving contiguous `range(168, 351)` in source:
  `stale_aggregate_range_351 = "".join(["range(168, ", "35", "1", ")"])`
- Include `stale_aggregate_range_351` in the stale aggregate tuple.
- Keep existing split stale aggregate guards, including `stale_aggregate_range_350`.
- Keep no-discovery-token guards for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk`.
- Keep the anchored `CURRENT_STATUS_PREFIX` assignment guard.

## Structure Health

No microrefactor. The touched files are intentionally narrow status-contract files, and the Phase 351 feature directory follows the established `design/codestable/features/YYYY-MM-DD-{slug}/` convention. The status test is long because it enumerates historical labels and stale guards; restructuring it would exceed this docs/static-test-only phase.

## Acceptance Criteria

- Only the four allowed files are changed.
- `attention.md` has exactly one current status line and it starts with `All phases 1-351 accepted`.
- Phase 351 label appears exactly once in attention and test required labels.
- Historical Phase 168-350 labels and `Phase 121-167` remain present.
- Focused test source contains live `range(168, 352)` and does not contain contiguous stale `range(168, 351)`.
- YAML validation, py_compile, focused pytest, and `git diff --check` pass.
- No `acceptance.md`, commit, stage, push, runtime, plugin, or config changes occur.

## Risk List

- Editing the nonexistent `tests/plugins/...` path would create a duplicate test and miss the real guard.
- Off-by-one range mistakes can omit Phase 351 or leave Phase 350 as the terminal contract.
- Adding stale range literals contiguously can make the self-guard fail.
- Terminal suffix edits can duplicate labels or leave the final `and` on Phase 350.
- Scope creep into runtime or acceptance finalization would violate the bounded phase.
