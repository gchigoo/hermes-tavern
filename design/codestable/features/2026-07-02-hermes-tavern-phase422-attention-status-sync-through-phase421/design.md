---
doc_type: feature-design
feature: 2026-07-02-hermes-tavern-phase422-attention-status-sync-through-phase421
title: "Phase 422 attention/status sync through Phase 421"
status: approved
implementation_ready: true
date: "2026-07-02"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 422 attention/status sync through accepted Phase 421; executor work is limited to status docs/tests plus non-final checklist handoff, with parent verification retaining acceptance/commit authority."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase422, company-boost]
---

# Phase 422 attention/status sync through Phase 421

## Current Evidence

Current evidence before S1:

- Branch `main` is at `4a5cb18` (`docs: accept tavern phase 421 status sync`), with the worker-observed tree clean.
- Phase 421 is accepted at HEAD, with accepted `design.md`, `checklist.yaml`, and `acceptance.md` under `design/codestable/features/2026-07-02-hermes-tavern-phase421-attention-status-sync-through-phase420/`.
- No Phase 422 feature directory existed at architect read time.
- `design/codestable/attention.md` is the startup attention source of truth and currently says `Current status (2026-06-18): All phases 1-421 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently guards the Phase 421 live status contract with current/stale prefixes for 421/420, required labels through Phase 421, terminal suffix through Phase 419/420/421, `range(168, 422)`, and split stale guards through `stale_aggregate_range_421`.

## Goals

- Materialize the Phase 422 feature `design.md` and `checklist.yaml` for this bounded company-boost S1 pass.
- Advance `design/codestable/attention.md` exactly one status tick from phases 1-421 accepted to phases 1-422 accepted.
- Append `Phase 422 attention status sync through Phase 421` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every existing required phase label, including the nonuniform Phase 168, 169, 170, 171, and 173 labels.
- Update `tests/test_hermes_tavern_codestable_status.py` to enforce the Phase 422 live status contract, including the new live range and stale split guards.
- Leave S2 acceptance/writeback for the parent controller only.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, cache, or service lifecycle changes.
- No acceptance artifact creation in this executor S1 pass.
- No staging, commit, push, dependency install, service start, credential access, or broad rewrite.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No adult-fiction/RP boundary change, minors-related work, CSAM behavior, or provider-safety-bypass behavior.
- No Phase 423 or later work.

## Allowed Files

This bounded pass may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-02-hermes-tavern-phase422-attention-status-sync-through-phase421/design.md`
- `design/codestable/features/2026-07-02-hermes-tavern-phase422-attention-status-sync-through-phase421/checklist.yaml`

`acceptance.md` must remain absent during this executor S1 pass. Parent/controller may create it later only after real verification gates pass and no commit/push has been performed by the worker.

## Exact Status And Test Contract

### attention.md

- Change the current prefix from `Current status (2026-06-18): All phases 1-421 accepted` to `Current status (2026-06-18): All phases 1-422 accepted`.
- Append exactly once: `Phase 422 attention status sync through Phase 421`.
- Preserve `Phase 121-167` and every existing `REQUIRED_PHASE_LABELS` entry, including:
  - `Phase 168 image settings JSON export`
  - `Phase 169 project JSON export surface parity`
  - `Phase 170 export command-surface regression`
  - `Phase 171 root-design export parity`
  - `Phase 173 root-design section 17 import/export summary parity`
- Preserve placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- End the status line with exactly: `Phase 420 attention status sync through Phase 419, Phase 421 attention status sync through Phase 420, and Phase 422 attention status sync through Phase 421.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-422 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-421 accepted"`
- `STALE_PHASE_MARKER = "1-421"`
- `STALE_PHASE_MARKER_EN_DASH = "1–421"`
- Append `"Phase 422 attention status sync through Phase 421"` to `REQUIRED_PHASE_LABELS` after Phase 421.
- Preserve every existing required label, including the nonuniform Phase 168, 169, 170, 171, and 173 labels.
- `FINAL_STATUS_SUFFIX = "Phase 420 attention status sync through Phase 419, Phase 421 attention status sync through Phase 420, and Phase 422 attention status sync through Phase 421."`
- `phase_range = range(168, 423)`
- `aggregate_range = "range(168, 423)"`
- Add `stale_aggregate_range_422 = "".join(["range(168, ", "42", "2", ")"])` and include it in the stale tuple.
- Preserve the prior split guard for stale `range(168, 421)` and ensure both direct stale `range(168, 422)` and direct stale `range(168, 421)` are rejected without embedding either stale direct literal contiguously in the test source.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not use naive substring counts.
- Preserve the status-line section-placement guard and all no-discovery-token guards.

## Verification Gates

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-02-hermes-tavern-phase422-attention-status-sync-through-phase421 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase422-executor python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static allowed-path/status/final-newline/trailing-whitespace guard covering changed plus untracked files.
- `git diff --check`
- If feasible: `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='`

## Parent Handoff Boundary

This is an executor S1 implementation pass only. Executor must leave `acceptance.md` absent, keep checklist/root acceptance states non-final, avoid staging/commit/push, and hand back to parent/controller for final verification, acceptance artifact creation, and any commit/push decision.
