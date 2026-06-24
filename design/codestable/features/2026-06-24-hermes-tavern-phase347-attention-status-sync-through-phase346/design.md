---
doc_type: feature-design
feature: 2026-06-24-hermes-tavern-phase347-attention-status-sync-through-phase346
status: approved
implementation_ready: true
date: "2026-06-24"
owner: company_boost_lane
lane: company-boost
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready Phase 347 attention/status sync through accepted Phase 346."
tags:
  - hermes-tavern
  - codestable
  - attention
  - status-sync
  - docs
  - tests
  - phase347
---

# Phase 347: Attention Status Sync Through Phase 346

## Background / Current Status

Phase 346 is the latest accepted phase. Its acceptance report is at:
`design/codestable/features/2026-06-24-hermes-tavern-phase346-attention-status-sync-through-phase345/acceptance.md` with status accepted.

Current live CodeStable status contract before S1:
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-346 accepted`.
- Terminal label is `Phase 346 attention status sync through Phase 345`.
- `tests/test_hermes_tavern_codestable_status.py` had:
  - `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-346 accepted"`
  - `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-345 accepted"`
  - `phase_range = range(168, 347)`
  - `aggregate_range = "range(168, 347)"`
- No Phase 348 feature directory existed before this slice.

## Goals

- Advance `design/codestable/attention.md` from 1-346 to 1-347.
- Append terminal label `Phase 347 attention status sync through Phase 346`.
- Update `tests/test_hermes_tavern_codestable_status.py` so focused status checks are for Phase 347.
- Preserve every historical label exactly, including `Phase 121-167` and all explicit `Phase 168` through `Phase 347` labels.
- Keep S1 executor-only scope and do not alter code/asset/runtime files.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/root docs/root design/architecture/roadmap/requirements/compound/build updates.
- No service lifecycle commands.
- No provider-safety bypasses.
- No minors/CSAM work and no adult-minor behavior changes.
- No acceptance.md creation in this S1.
- No Phase 348 work.

## Exact Allowed Files

- `design/codestable/features/2026-06-24-hermes-tavern-phase347-attention-status-sync-through-phase346/design.md`
- `design/codestable/features/2026-06-24-hermes-tavern-phase347-attention-status-sync-through-phase346/checklist.yaml`
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

## Status test contract

### attention.md

- Update prefix exactly to:
  - `Current status (2026-06-18): All phases 1-347 accepted`
- Append exactly once:
  - `Phase 347 attention status sync through Phase 346`
- Replace terminal suffix to exactly:
  - `Phase 345 attention status sync through Phase 344, Phase 346 attention status sync through Phase 345, and Phase 347 attention status sync through Phase 346.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-347 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-346 accepted"`
- `STALE_PHASE_MARKER = "1-346"`
- `STALE_PHASE_MARKER_EN_DASH = "1–346"`
- `REQUIRED_PHASE_LABELS` includes `"Phase 347 attention status sync through Phase 346"` exactly once after Phase 346.
- `FINAL_STATUS_SUFFIX = "Phase 345 attention status sync through Phase 344, Phase 346 attention status sync through Phase 345, and Phase 347 attention status sync through Phase 346."`
- `phase_range = range(168, 348)`
- `aggregate_range = "range(168, 348)"`
- Add and include in stale aggregate tuple:
  - `stale_aggregate_range_347 = "".join(["range(168, ", "34", "7", ")"])`
- Keep no-discovery-token guards.
- Keep one anchored CURRENT_STATUS_PREFIX guard.
- Ensure no contiguous stale terminal literal `range(168, 347)` appears except through split forms.

## Verification commands

```bash
PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-24-hermes-tavern-phase347-attention-status-sync-through-phase346 --require doc_type --require status --require feature
PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider
git diff --check
```

Optional:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider
```

## Executor prompt

`Executor S1: implement docs+test status-sync only; allowed files are design.md, checklist.yaml, attention.md, tests/test_hermes_tavern_codestable_status.py; no acceptance.md; no phase 348; no commit/push`

This is non-final S1. No `acceptance.md` and no Phase 348 files are created.
