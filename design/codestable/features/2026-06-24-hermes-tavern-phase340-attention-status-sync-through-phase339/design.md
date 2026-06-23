---
doc_type: feature-design
status: approved
workflow_status: ready_for_executor
feature: 2026-06-24-hermes-tavern-phase340-attention-status-sync-through-phase339
date: "2026-06-24"
owner: standard_lane
lane: standard/personal
bounded_phase: "docs/static-test/status-only"
implementation_ready: true
result_type: status_sync_s1
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase340]
summary: "Implementation-ready S1 status sync advancing CodeStable attention and focused status regression through accepted Phase 339."
---

# Phase 340: Attention Status Sync Through Phase 339

## Gate

- Phase 339 acceptance exists at `design/codestable/features/2026-06-23-hermes-tavern-phase339-attention-status-sync-through-phase338/acceptance.md` with `status: accepted`.
- Current live `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-339 accepted`.
- Current focused status test is synced through Phase 339 with `phase_range = range(168, 340)` and `aggregate_range = "range(168, 340)"`.
- No Phase 340 feature directory currently exists.
- No higher-confidence unfinished ready-for-executor feature/checklist was identified in the bounded recent lane check.
- The standard/personal lane can process at most one bounded slice, and this recurring docs/static-test/status-only attention/status regression slice remains the safest next slice.

## Goals

- Create the Phase 340 feature artifacts and execute the bounded S1 status sync.
- Advance `design/codestable/attention.md` exactly one phase, from 1-339 to 1-340.
- Update `tests/test_hermes_tavern_codestable_status.py` so the static regression guards the Phase 340 live status contract.
- Preserve all existing historical labels, including `Phase 121-167` and explicit Phase 168-339 labels.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root README, root design, architecture, roadmap, requirements, or compound changes.
- No Hermes-native plugin architecture changes and no SillyTavern asset compatibility changes.
- No minors-related work and no provider-safety bypass.
- No commits, staging, pushes, service lifecycle commands, or dependency installation.

## Exact S1 Live Contract

- New attention prefix:
  - `Current status (2026-06-18): All phases 1-340 accepted`
- New terminal label:
  - `Phase 340 attention status sync through Phase 339`
- Stale prefix/markers after update:
  - `Current status (2026-06-18): All phases 1-339 accepted`
  - `1-339`
  - `1–339`
- Focused test range values:
  - `phase_range = range(168, 341)`
  - `aggregate_range = "range(168, 341)"`
- Split stale aggregate guard:
  - Guard stale `range(168, 340)` through split string construction in the test source.
  - Do not leave a contiguous stale `range(168, 340)` literal in `tests/test_hermes_tavern_codestable_status.py`.

## Required Status Test Shape

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-340 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-339 accepted"`
- `STALE_PHASE_MARKER = "1-339"`
- `STALE_PHASE_MARKER_EN_DASH = "1–339"`
- `REQUIRED_PHASE_LABELS` includes `Phase 340 attention status sync through Phase 339` exactly once and preserves all existing labels.
- `FINAL_STATUS_SUFFIX` ends with:
  - `Phase 338 attention status sync through Phase 337, Phase 339 attention status sync through Phase 338, and Phase 340 attention status sync through Phase 339.`
- `phase_range = range(168, 341)`
- `aggregate_range = "range(168, 341)"`
- Add `stale_aggregate_range_340` via split pieces such as `["range(168, ", "34", "0", ")"]`, include it in the stale-range tuple, and retain older split stale aggregate guards.
- Preserve the anchored single-assignment guard for `CURRENT_STATUS_PREFIX`.
- Preserve no-discovery-token guards for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk`.

## Allowed Files

S1 executor may touch exactly:

- `design/codestable/features/2026-06-24-hermes-tavern-phase340-attention-status-sync-through-phase339/design.md`
- `design/codestable/features/2026-06-24-hermes-tavern-phase340-attention-status-sync-through-phase339/checklist.yaml`
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

If and only if controller finalizes S2 after verification, it may additionally create:

- `design/codestable/features/2026-06-24-hermes-tavern-phase340-attention-status-sync-through-phase339/acceptance.md`

## Verification

Required S1/S2 gates:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-24-hermes-tavern-phase340-attention-status-sync-through-phase339 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static guard for allowed files, protected paths, stale markers, no-discovery tokens, final newline, and trailing whitespace.
- `git diff --check`
- Full suite when feasible: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider`

## Executor Instruction

Implement only this Phase 340 status sync. Do not broaden scope, do not edit protected files, do not create acceptance before verification, and do not commit/stage/push.