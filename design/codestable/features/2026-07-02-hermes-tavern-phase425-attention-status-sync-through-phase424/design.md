---
doc_type: feature-design
feature: 2026-07-02-hermes-tavern-phase425-attention-status-sync-through-phase424
title: "Phase 425 attention/status sync through Phase 424"
status: approved
implementation_ready: true
date: "2026-07-02"
owner: standard-lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 425 attention/status sync through accepted Phase 424; executor work is limited to status docs/tests plus non-final checklist handoff, with parent verification retaining acceptance/commit authority."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase425, standard-lane]
---

# Phase 425 attention/status sync through Phase 424

## Current Evidence

Current evidence before S1:

- Branch `main` is at `7e8c8bc6fdc2562f1365ca5513ecfffea01d0c75` (`docs: accept tavern phase 424 status sync`), with the controller-confirmed tree clean.
- Phase 424 is accepted at HEAD, with accepted `design.md`, `checklist.yaml`, and `acceptance.md` under `design/codestable/features/2026-07-02-hermes-tavern-phase424-attention-status-sync-through-phase423/`.
- No Phase 425 feature directory existed at architect read time.
- `design/codestable/attention.md` is the startup attention source of truth and currently says `Current status (2026-06-18): All phases 1-424 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently guards the Phase 424 live status contract with current/stale prefixes for 424/423, required labels through Phase 424, terminal suffix through Phase 422/423/424, the live aggregate range ending at 425, and split stale guards through `stale_aggregate_range_424`.

## Goals

- Materialize the Phase 425 feature `design.md` and `checklist.yaml` for this bounded standard-lane S1 pass.
- Advance `design/codestable/attention.md` exactly one status tick from phases 1-424 accepted to phases 1-425 accepted.
- Append `Phase 425 attention status sync through Phase 424` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every existing required phase label, including the nonuniform Phase 168, 169, 170, 171, and 173 labels.
- Update `tests/test_hermes_tavern_codestable_status.py` to enforce the Phase 425 live status contract, including the new live range and stale split guards.
- Leave S2 acceptance/writeback for the parent controller only.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, cache, or service lifecycle changes.
- No acceptance artifact creation in this executor S1 pass.
- No staging, commit, push, dependency install, service start, credential access, or broad rewrite.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No adult-fiction/RP boundary change, minors-related work, CSAM behavior, or provider-safety-bypass behavior.
- No Phase 426 or later work.

## Allowed Files

This bounded pass may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-02-hermes-tavern-phase425-attention-status-sync-through-phase424/design.md`
- `design/codestable/features/2026-07-02-hermes-tavern-phase425-attention-status-sync-through-phase424/checklist.yaml`

`acceptance.md` must remain absent during this executor S1 pass. Parent/controller may create it later only after real verification gates pass and no commit/push has been performed by the worker.

## Exact Status And Test Contract

### attention.md

- Change the current prefix from `Current status (2026-06-18): All phases 1-424 accepted` to `Current status (2026-06-18): All phases 1-425 accepted`.
- Append exactly once: `Phase 425 attention status sync through Phase 424`.
- Preserve `Phase 121-167` and every existing `REQUIRED_PHASE_LABELS` entry, including:
  - `Phase 168 image settings JSON export`
  - `Phase 169 project JSON export surface parity`
  - `Phase 170 export command-surface regression`
  - `Phase 171 root-design export parity`
  - `Phase 173 root-design section 17 import/export summary parity`
- Preserve placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- End the status line with exactly: `Phase 423 attention status sync through Phase 422, Phase 424 attention status sync through Phase 423, and Phase 425 attention status sync through Phase 424.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-425 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-424 accepted"`
- `STALE_PHASE_MARKER = "1-424"`
- `STALE_PHASE_MARKER_EN_DASH = "1–424"`
- Append `"Phase 425 attention status sync through Phase 424"` to `REQUIRED_PHASE_LABELS` after Phase 424.
- Preserve every existing required label, including the nonuniform Phase 168, 169, 170, 171, and 173 labels.
- `FINAL_STATUS_SUFFIX = "Phase 423 attention status sync through Phase 422, Phase 424 attention status sync through Phase 423, and Phase 425 attention status sync through Phase 424."`
- `phase_range = range(168, 426)`
- `aggregate_range = "range(168, 426)"`
- Add `stale_aggregate_range_425 = "".join(["range(168, ", "42", "5", ")"])` and include it in the stale tuple.
- Preserve stale split guards through 424, and preserve stale direct-literal rejection for 424/423/422/421 while adding the 425 rejection without embedding direct stale literals contiguously in the test source.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not use naive substring counts.
- Preserve the status-line section-placement guard, all-label guard, and no `.glob`/`.rglob`/`iterdir`/`os.walk` discovery-token guards.

## Verification Gates

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-02-hermes-tavern-phase425-attention-status-sync-through-phase424 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase425-executor python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static allowed-path/status/final-newline/trailing-whitespace guard covering changed plus untracked files.
- `git diff --check`
- If feasible: `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='`

## Parent Handoff Boundary

This is an executor S1 implementation pass only. Executor must leave `acceptance.md` absent, keep checklist/root acceptance states non-final, avoid staging/commit/push, and hand back to parent/controller for final verification, acceptance artifact creation, and any commit/push decision.
