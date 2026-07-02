---
doc_type: feature-design
feature: 2026-07-02-hermes-tavern-phase420-attention-status-sync-through-phase419
title: "Phase 420 attention/status sync through Phase 419"
status: approved
implementation_ready: true
date: "2026-07-02"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 420 attention/status sync through accepted Phase 419; executor work is limited to status docs/tests plus non-final checklist handoff, with parent verification retaining acceptance/commit authority."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase420, company-boost]
---

# Phase 420 attention/status sync through Phase 419

## Current Evidence

Current evidence before S1:

- Branch `main` is clean at `HEAD`, with Phase 419 already accepted by the prior bounded slice.
- Phase 419 is accepted, with accepted `checklist.yaml` and `acceptance.md` under `design/codestable/features/2026-07-02-hermes-tavern-phase419-attention-status-sync-through-phase418/`.
- No Phase 420 feature directory existed before this bounded slice.
- `design/codestable/attention.md` is the startup attention source of truth and currently says `Current status (2026-06-18): All phases 1-419 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently guards the Phase 419 live status contract with `range(168, 420)` and split stale guards for prior ranges.

## Goals

- Create the Phase 420 feature `design.md` and `checklist.yaml` for this bounded company-boost S1 pass.
- Advance `design/codestable/attention.md` exactly one status tick from phases 1-419 accepted to phases 1-420 accepted.
- Append `Phase 420 attention status sync through Phase 419` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 419 label already present in the attention status line and focused regression.
- Update `tests/test_hermes_tavern_codestable_status.py` to enforce the Phase 420 live status contract, including the new live range and stale split guards.
- Leave S2 acceptance/writeback for the parent controller only.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache changes.
- No acceptance artifact creation in this executor S1 pass.
- No staging, commit, push, dependency install, service start, or broad rewrite.
- No Hermes-native plugin architecture, SillyTavern asset compatibility, or adult-fiction/RP boundary changes.
- No minors, CSAM, or provider-safety-bypass behavior.
- No Phase 421 or later work.

## Allowed Files

This bounded pass may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-02-hermes-tavern-phase420-attention-status-sync-through-phase419/design.md`
- `design/codestable/features/2026-07-02-hermes-tavern-phase420-attention-status-sync-through-phase419/checklist.yaml`

`acceptance.md` must remain absent during this executor S1 pass. Parent/controller may create it later only after real verification gates pass and no commit/push has been performed by the worker.

## Exact Status And Test Contract

### attention.md

- Change the current prefix from `Current status (2026-06-18): All phases 1-419 accepted` to `Current status (2026-06-18): All phases 1-420 accepted`.
- Append exactly once: `Phase 420 attention status sync through Phase 419`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 419 label.
- Preserve the special non-recurring labels exactly: `Phase 168 image settings JSON export`, `Phase 169 project JSON export surface parity`, `Phase 170 export command-surface regression`, `Phase 171 root-design export parity`, and `Phase 173 root-design section 17 import/export summary parity`.
- Preserve placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- End the status line with exactly: `Phase 418 attention status sync through Phase 417, Phase 419 attention status sync through Phase 418, and Phase 420 attention status sync through Phase 419.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-420 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-419 accepted"`
- `STALE_PHASE_MARKER = "1-419"`
- `STALE_PHASE_MARKER_EN_DASH = "1–419"`
- Append `"Phase 420 attention status sync through Phase 419"` to `REQUIRED_PHASE_LABELS` after Phase 419.
- `FINAL_STATUS_SUFFIX = "Phase 418 attention status sync through Phase 417, Phase 419 attention status sync through Phase 418, and Phase 420 attention status sync through Phase 419."`
- `phase_range = range(168, 421)`
- `aggregate_range = "range(168, 421)"`
- Add `stale_aggregate_range_420 = "".join(["range(168, ", "42", "0", ")"])` and include it in the stale tuple while preserving `stale_aggregate_range_419` and earlier.
- Keep the final dynamic stale guards rejecting stale `range(168, 420)` and `range(168, 419)` without embedding either stale literal contiguously in the test source.
- Preserve anchored single-assignment guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.
- Preserve the status placement guard and no-discovery-token guards.

## Verification Gates

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-02-hermes-tavern-phase420-attention-status-sync-through-phase419 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase420-exec python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- `git diff --check`
- `git status --short --branch --untracked-files=all`

## Parent Handoff Boundary

This is an executor S1 implementation pass only. Parent/controller verification owns final acceptance, any acceptance artifact creation, any accepted checklist writeback, and any commit/push decision. Executor must leave `parent_commit_or_push_performed: false` and must not stage, commit, or push.
