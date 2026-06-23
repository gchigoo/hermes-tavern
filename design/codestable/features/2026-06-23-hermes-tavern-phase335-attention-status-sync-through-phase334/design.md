---
doc_type: feature-design
status: approved
workflow_status: ready_for_executor
feature: 2026-06-23-hermes-tavern-phase335-attention-status-sync-through-phase334
date: "2026-06-23"
owner: standard_lane
lane: standard/personal
bounded_phase: "docs/static-test/status-only"
implementation_ready: true
result_type: status_sync_s1
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase335]
summary: "Implementation-ready S1 status sync advancing CodeStable attention and focused status regression through accepted Phase 334."
---

# Phase 335: Attention Status Sync Through Phase 334

## Gate

- Phase 334 acceptance exists at `design/codestable/features/2026-06-23-hermes-tavern-phase334-attention-status-sync-through-phase333/acceptance.md` with `status: accepted`.
- Current live `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-334 accepted`.
- Current focused status test is synced through Phase 334 with `phase_range = range(168, 335)` and `aggregate_range = "range(168, 335)"`.
- No Phase 335 feature directory currently exists.
- Older Phase 326 has stale pending subfields in its checklist, but its checklist top-level status and acceptance report are accepted, and later Phases 327-334 are accepted; it is not a safer active slice.

## Goals

- Create the Phase 335 feature artifacts and execute the bounded S1 status sync.
- Advance `design/codestable/attention.md` exactly one phase, from 1-334 to 1-335.
- Update `tests/test_hermes_tavern_codestable_status.py` so the static regression guards the Phase 335 live status contract.
- Preserve all existing historical labels, including `Phase 121-167` and explicit Phase 168-334 labels.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root README, root design, architecture, roadmap, requirements, or compound changes.
- No Hermes-native plugin architecture changes and no SillyTavern asset compatibility changes.
- No minors-related work and no provider-safety bypass.
- No commits, staging, pushes, service lifecycle commands, or dependency installation.

## Exact S1 Live Contract

- New attention prefix:
  - `Current status (2026-06-18): All phases 1-335 accepted`
- New terminal label:
  - `Phase 335 attention status sync through Phase 334`
- Stale prefix/markers after update:
  - `Current status (2026-06-18): All phases 1-334 accepted`
  - `1-334`
  - `1–334`
- Focused test range values:
  - `phase_range = range(168, 336)`
  - `aggregate_range = "range(168, 336)"`
- Split stale aggregate guard:
  - Guard stale `range(168, 335)` through split string construction in the test source.
  - Do not leave a contiguous stale `range(168, 335)` literal in `tests/test_hermes_tavern_codestable_status.py`.

## Required Status Test Shape

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-335 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-334 accepted"`
- `STALE_PHASE_MARKER = "1-334"`
- `STALE_PHASE_MARKER_EN_DASH = "1–334"`
- `REQUIRED_PHASE_LABELS` includes `Phase 335 attention status sync through Phase 334` exactly once and preserves all existing labels.
- `FINAL_STATUS_SUFFIX` ends with:
  - `Phase 333 attention status sync through Phase 332, Phase 334 attention status sync through Phase 333, and Phase 335 attention status sync through Phase 334.`
- `phase_range = range(168, 336)`
- `aggregate_range = "range(168, 336)"`
- Add `stale_aggregate_range_335` via split pieces such as `["range(168, ", "33", "5", ")"]`, include it in the stale-range tuple, and retain older split stale aggregate guards.
- Preserve the anchored single-assignment guard for `CURRENT_STATUS_PREFIX`.
- Preserve no-discovery-token guards for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk`.

## Allowed Files

S1 executor may touch exactly:

- `design/codestable/features/2026-06-23-hermes-tavern-phase335-attention-status-sync-through-phase334/design.md`
- `design/codestable/features/2026-06-23-hermes-tavern-phase335-attention-status-sync-through-phase334/checklist.yaml`
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

If and only if controller finalizes S2 in the same tick after verification, it may additionally create:

- `design/codestable/features/2026-06-23-hermes-tavern-phase335-attention-status-sync-through-phase334/acceptance.md`

## Verification

Required S1/S2 gates:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-23-hermes-tavern-phase335-attention-status-sync-through-phase334 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static guard for allowed files, protected paths, stale markers, no-discovery tokens, final newline, and trailing whitespace.
- `git diff --check`
- Full suite when feasible: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider`

## Executor Instruction

Implement only this Phase 335 status sync. Do not broaden scope, do not edit protected files, do not create acceptance before verification, and do not commit/stage/push.
