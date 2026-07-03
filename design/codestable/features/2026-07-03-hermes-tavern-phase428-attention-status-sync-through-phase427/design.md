---
doc_type: feature-design
feature: 2026-07-03-hermes-tavern-phase428-attention-status-sync-through-phase427
title: "Phase 428 attention/status sync through Phase 427"
status: approved
implementation_ready: true
date: "2026-07-03"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 428 attention/status sync through accepted Phase 427; executor work is limited to status docs/tests plus non-final checklist handoff, with parent verification retaining acceptance/commit authority."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase428, company-boost]
---

# Phase 428 attention/status sync through Phase 427

## Current Evidence

Current evidence before S1:

- Branch `main` is at `4817d85b19c83f0c02196a9389757025a0d422f5`, with the controller-confirmed tree clean before this feature directory was created.
- Phase 427 is accepted at HEAD, with accepted `design.md`, `checklist.yaml`, and `acceptance.md` under `design/codestable/features/2026-07-03-hermes-tavern-phase427-attention-status-sync-through-phase426/`.
- No Phase 428 feature directory existed at architect read time.
- `design/codestable/attention.md` is the startup attention source of truth and currently says `Current status (2026-06-18): All phases 1-427 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently guards the Phase 427 live status contract with current/stale prefixes for 427/426, required labels through Phase 427, terminal suffix through 425/426/427, the live aggregate range ending at 428, split stale guards through `stale_aggregate_range_427`, and direct stale guards for 427/426/425/424/423/422/421.

## Goals

- Materialize the Phase 428 feature `design.md` and `checklist.yaml` for this bounded company-boost S1 pass.
- Advance `design/codestable/attention.md` exactly one status tick from phases 1-427 accepted to phases 1-428 accepted.
- Append `Phase 428 attention status sync through Phase 427` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every existing required phase label, especially all explicit Phase 168-427 labels.
- Update `tests/test_hermes_tavern_codestable_status.py` to enforce the Phase 428 live status contract, including the new live range and stale split/direct guards.
- Leave S2 acceptance/writeback for the parent controller only.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, cache, or service lifecycle changes.
- No acceptance artifact creation in this executor S1 pass.
- No staging, commit, push, dependency install, service start, credential access, or broad rewrite.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No adult-fiction/RP boundary change, minor-related sexual content, CSAM behavior, or provider safety bypass.
- No Phase 429 or later work.

## Allowed Files

This bounded pass may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-03-hermes-tavern-phase428-attention-status-sync-through-phase427/design.md`
- `design/codestable/features/2026-07-03-hermes-tavern-phase428-attention-status-sync-through-phase427/checklist.yaml`

`acceptance.md` must remain absent during this executor S1 pass. Parent/controller may create it later only after real verification gates pass and no commit/push has been performed by the worker.

## Exact Status And Test Contract

### attention.md

- Change the current prefix from `Current status (2026-06-18): All phases 1-427 accepted` to `Current status (2026-06-18): All phases 1-428 accepted`.
- Append exactly once: `Phase 428 attention status sync through Phase 427`.
- Preserve `Phase 121-167` and every existing `REQUIRED_PHASE_LABELS` entry, including the nonuniform Phase 168, 169, 170, 171, and 173 labels and the recent Phase 426/427 labels.
- Preserve placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- End the status line with exactly: `Phase 426 attention status sync through Phase 425, Phase 427 attention status sync through Phase 426, and Phase 428 attention status sync through Phase 427.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-428 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-427 accepted"`
- `STALE_PHASE_MARKER = "1-427"`
- `STALE_PHASE_MARKER_EN_DASH = "1–427"`
- Append `"Phase 428 attention status sync through Phase 427"` to `REQUIRED_PHASE_LABELS` after Phase 427.
- Preserve every existing required label, including the nonuniform Phase 168, 169, 170, 171, and 173 labels and the Phase 121-167 aggregate label.
- `FINAL_STATUS_SUFFIX = "Phase 426 attention status sync through Phase 425, Phase 427 attention status sync through Phase 426, and Phase 428 attention status sync through Phase 427."`
- `phase_range = range(168, 429)`
- `aggregate_range = "range(168, 429)"`
- Add `stale_aggregate_range_428 = "".join(["range(168, ", "42", "8", ")"])` and include it in the stale tuple.
- Add direct stale guard `stale_aggregate_guard_428 = "".join(["range(168, ", "42", str(8), ")"])` and assert it is absent from the test source.
- Preserve direct stale guards for 427/426/425/424/423/422/421.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not use naive substring counts.
- Preserve the status-line section-placement guard, all-label guard, and no `.glob`/`.rglob`/`iterdir`/`os.walk` discovery-token guards.

## Verification Gates

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-03-hermes-tavern-phase428-attention-status-sync-through-phase427 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase428-controller python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static allowed-path/status/final-newline/trailing-whitespace guard covering changed plus untracked files.
- `git diff --check`
- If feasible: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider`

## Parent Handoff Boundary

This is an executor S1 implementation pass only. Executor must leave `acceptance.md` absent, keep checklist/root acceptance states non-final, avoid staging/commit/push, and hand back to parent/controller for final verification, acceptance artifact creation, and any commit/push decision.
