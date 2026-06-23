---
doc_type: feature-design
feature: 2026-06-23-hermes-tavern-phase332-attention-status-sync-through-phase331
status: accepted
date: "2026-06-23"
owner: company_boost_lane
lane: company-boost/parent-verified-artifact
implementation_ready: true
bounded_phase: "docs/static-test/status-only"
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase332]
summary: "Close out Phase 332 status-sync after worker verification and advance attention/status through accepted Phase 331."
---

# Phase 332: CodeStable Attention Status Sync Through Phase 331

## Gate

Phase 331 is accepted at `design/codestable/features/2026-06-23-hermes-tavern-phase331-attention-status-sync-through-phase330/acceptance.md`.

Current state before closeout:
- `design/codestable/attention.md` reported `Current status (2026-06-18): All phases 1-331 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` enforced the Phase 331 contract.

Current and final state:
- `design/codestable/attention.md` and focused status test advance to the Phase 332 closeout contract.
- `acceptance.md` is materialized for S2 closeout evidence.

## Goals

- Advance the attention status line to Phase 332.
- Add `Phase 332 attention status sync through Phase 331` once, preserving prior labels.
- Keep all existing runtime/source/plugin/provider/gateway/CLI behavior unchanged.
- Preserve all required non-status project constraints (no runtime/provider/plugin/network/dependency/config edits).
- Capture exact verification evidence and close out checklist/acceptance as accepted.

## Exact Status Contract

Advance the `attention.md` current-status prefix to:
- `Current status (2026-06-18): All phases 1-332 accepted`

Add/retain exactly once:
- `Phase 332 attention status sync through Phase 331`

Final attention status suffix:
- `Phase 329 attention status sync through Phase 328, Phase 330 attention status sync through Phase 329, Phase 331 attention status sync through Phase 330, and Phase 332 attention status sync through Phase 331.`

Preserve through this sequence:
- `Phase 121-167`
- All explicit labels `Phase 168` through `Phase 332`.

## Focused Test Contract

Finalized `tests/test_hermes_tavern_codestable_status.py` contract:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-332 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-331 accepted"`
- `STALE_PHASE_MARKER = "1-331"`
- `STALE_PHASE_MARKER_EN_DASH = "1–331"`
- `phase_range = range(168, 333)`
- `aggregate_range = "range(168, 333)"`
- `FINAL_STATUS_SUFFIX` ends exactly with `Phase 332 attention status sync through Phase 331.` with exactly one final `and`.
- `REQUIRED_PHASE_LABELS` contains `Phase 332 attention status sync through Phase 331` exactly once.
- Split stale aggregate guard for `range(168, 332)` is present in split-string form and is included in stale loop.
- Preserve older split stale aggregate guards.
- Keep anchored assignment guard and no discovery-token tokens (`.glob(`, `.rglob(`, `iterdir(`, `os.walk`).

## Allowed Files

Executor/parent-allowed files:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-23-hermes-tavern-phase332-attention-status-sync-through-phase331/design.md`
- `design/codestable/features/2026-06-23-hermes-tavern-phase332-attention-status-sync-through-phase331/checklist.yaml`
- `design/codestable/features/2026-06-23-hermes-tavern-phase332-attention-status-sync-through-phase331/acceptance.md`

## Execution

1. Apply status/test/list updates in allowed files.
2. Validate exact contract and stale markers/ranges.
3. Run required verification commands.
4. Update checklist and acceptance to accepted state.

## Verification Commands

Run from repo root:

```bash
PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-23-hermes-tavern-phase332-attention-status-sync-through-phase331 --require doc_type --require status --require feature
PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider
git diff --check
```
