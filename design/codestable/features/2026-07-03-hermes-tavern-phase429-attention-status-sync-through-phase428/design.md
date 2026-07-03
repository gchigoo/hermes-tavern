---
doc_type: feature-design
feature: 2026-07-03-hermes-tavern-phase429-attention-status-sync-through-phase428
title: "Phase 429 attention/status sync through Phase 428"
status: approved
implementation_ready: true
date: "2026-07-03"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 429 attention/status sync through accepted Phase 428; executor work is limited to status docs/tests plus non-final checklist handoff, with parent verification retaining acceptance/commit authority."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase429, company-boost]
---

# Phase 429 attention/status sync through Phase 428

## Current Evidence

Current evidence before S1:

- Branch `main` is at `f163f5c9a1a33442616a4663a5c9e1c19c333291`, with the controller-confirmed tree clean before this feature directory was created.
- Latest accepted slice is `docs: accept tavern phase 428 status sync`.
- Phase 428 is accepted, with accepted `design.md`, `checklist.yaml`, and `acceptance.md` under `design/codestable/features/2026-07-03-hermes-tavern-phase428-attention-status-sync-through-phase427/`.
- No Phase 429 feature directory existed at architect read time.
- `design/codestable/attention.md` is the startup attention source of truth and currently says `Current status (2026-06-18): All phases 1-428 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently guards the Phase 428 live status contract with current/stale prefixes for 428/427, required labels through Phase 428, terminal suffix through 426/427/428, the live aggregate range ending at 429, split stale guards through `stale_aggregate_range_428`, and direct stale guards for 428/427/426/425/424/423/422/421.

## Goals

- Materialize the Phase 429 feature `design.md` and `checklist.yaml` for this bounded company-boost S1 pass.
- Advance `design/codestable/attention.md` exactly one status tick from phases 1-428 accepted to phases 1-429 accepted.
- Append `Phase 429 attention status sync through Phase 428` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every existing required phase label, especially all explicit Phase 168-428 labels.
- Update `tests/test_hermes_tavern_codestable_status.py` to enforce the Phase 429 live status contract, including the new live range and stale split/direct guards.
- Leave S2 acceptance/writeback for the parent controller only.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, cache, or service lifecycle changes.
- No acceptance artifact creation in this executor S1 pass.
- No staging, commit, push, dependency install, service start, credential access, or broad rewrite.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No adult-fiction/RP boundary change, minor-related sexual content, CSAM behavior, or provider safety bypass.
- No Phase 430 or later work.

## Allowed Files

This bounded pass may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-03-hermes-tavern-phase429-attention-status-sync-through-phase428/design.md`
- `design/codestable/features/2026-07-03-hermes-tavern-phase429-attention-status-sync-through-phase428/checklist.yaml`

`acceptance.md` must remain absent during this executor S1 pass. Parent/controller may create it later only after real verification gates pass and no commit/push has been performed by the worker.

## Exact Status And Test Contract

### attention.md

- Change the current prefix from `Current status (2026-06-18): All phases 1-428 accepted` to `Current status (2026-06-18): All phases 1-429 accepted`.
- Append exactly once: `Phase 429 attention status sync through Phase 428`.
- Preserve `Phase 121-167` and every existing `REQUIRED_PHASE_LABELS` entry, including the nonuniform Phase 168, 169, 170, 171, and 173 labels and the recent Phase 427/428 labels.
- Preserve placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- End the status line with exactly: `Phase 427 attention status sync through Phase 426, Phase 428 attention status sync through Phase 427, and Phase 429 attention status sync through Phase 428.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-429 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-428 accepted"`
- `STALE_PHASE_MARKER = "1-428"`
- `STALE_PHASE_MARKER_EN_DASH = "1–428"`
- Append `"Phase 429 attention status sync through Phase 428"` to `REQUIRED_PHASE_LABELS` after Phase 428.
- Preserve every existing required label, including the nonuniform Phase 168, 169, 170, 171, and 173 labels and the Phase 121-167 aggregate label.
- `FINAL_STATUS_SUFFIX = "Phase 427 attention status sync through Phase 426, Phase 428 attention status sync through Phase 427, and Phase 429 attention status sync through Phase 428."`
- `phase_range = range(168, 430)`
- `aggregate_range = "range(168, 430)"`
- Add `stale_aggregate_range_429 = "".join(["range(168, ", "42", "9", ")"])` and include it in the stale tuple.
- Add direct stale guard `stale_aggregate_guard_429 = "".join(["range(168, ", "42", str(9), ")"])` and assert it is absent from the test source.
- Preserve direct stale guards for 428/427/426/425/424/423/422/421.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not use naive substring counts.
- Preserve the status-line section-placement guard, all-label guard, and no `.glob`/`.rglob`/`iterdir`/`os.walk` discovery-token guards.

## Verification Gates

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-03-hermes-tavern-phase429-attention-status-sync-through-phase428 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase429-worker python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static allowed-path/status/final-newline/trailing-whitespace guard covering changed plus untracked files.
- `git diff --check`
- Parent may run broader pytest during closeout.

## Parent Handoff Boundary

This is an executor S1 implementation pass only. Executor must leave `acceptance.md` absent, keep checklist/root acceptance states non-final, avoid staging/commit/push, and hand back to parent/controller for final verification, acceptance artifact creation, and any commit/push decision.
