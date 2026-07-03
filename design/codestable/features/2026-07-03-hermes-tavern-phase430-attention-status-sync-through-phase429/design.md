---
doc_type: feature-design
feature: 2026-07-03-hermes-tavern-phase430-attention-status-sync-through-phase429
title: "Phase 430 attention/status sync through Phase 429"
status: approved
implementation_ready: true
date: "2026-07-03"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 430 attention/status sync through accepted Phase 429; executor work is limited to status docs/tests plus non-final checklist handoff, with parent verification retaining acceptance authority."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase430, company-boost]
---

# Phase 430 attention/status sync through Phase 429

## Current Evidence

- Branch `main` is at `6760e8b`, with controller preflight reporting a clean tree.
- Recent accepted commits are Phase 429 (`6760e8b`), Phase 428 (`f163f5c`), and Phase 427 (`4817d85`).
- Phase 429 is accepted, with accepted `design.md`, `checklist.yaml`, and `acceptance.md` under `design/codestable/features/2026-07-03-hermes-tavern-phase429-attention-status-sync-through-phase428/`.
- No Phase 430 feature directory existed at architect read time.
- `design/codestable/attention.md` currently says `Current status (2026-06-18): All phases 1-429 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently guards the Phase 429 live contract with current/stale prefixes for 429/428, required labels through Phase 429, terminal suffix through 427/428/429, live aggregate range ending at 430, split stale guards through `stale_aggregate_range_429`, and direct stale guards for 429/428/427/426/425/424/423/422/421.

## Goals

- Materialize the Phase 430 feature `design.md` and `checklist.yaml`.
- Advance `design/codestable/attention.md` exactly one tick from phases 1-429 accepted to phases 1-430 accepted.
- Append `Phase 430 attention status sync through Phase 429` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every existing Phase 168-429 required label exactly as currently represented.
- Update `tests/test_hermes_tavern_codestable_status.py` to enforce the Phase 430 live status contract.
- Leave S2 verification and acceptance closeout for the parent controller.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, cache, or service lifecycle changes.
- No acceptance artifact creation in S1.
- No staging, commit, push, dependency install, service start, credential access, or broad rewrite.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No adult-fiction/RP boundary change, minor-related sexual content, CSAM behavior, or provider safety bypass.
- No Phase 431 or later work.

## Allowed Files

Only these files may change or appear as untracked files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-03-hermes-tavern-phase430-attention-status-sync-through-phase429/design.md`
- `design/codestable/features/2026-07-03-hermes-tavern-phase430-attention-status-sync-through-phase429/checklist.yaml`

`acceptance.md` must remain absent during S1 and must not be accepted before parent closeout.

## Exact Status And Test Contract

### attention.md

- Remove stale live prefix: `Current status (2026-06-18): All phases 1-429 accepted`.
- Require live prefix: `Current status (2026-06-18): All phases 1-430 accepted`.
- Append exactly once: `Phase 430 attention status sync through Phase 429`.
- Preserve every prior Phase 168-429 label exactly as currently represented; do not synthesize labels.
- Preserve placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- End the status line with exactly: `Phase 428 attention status sync through Phase 427, Phase 429 attention status sync through Phase 428, and Phase 430 attention status sync through Phase 429.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-430 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-429 accepted"`
- `STALE_PHASE_MARKER = "1-429"`
- `STALE_PHASE_MARKER_EN_DASH = "1–429"`
- Append `"Phase 430 attention status sync through Phase 429"` after Phase 429 in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 428 attention status sync through Phase 427, Phase 429 attention status sync through Phase 428, and Phase 430 attention status sync through Phase 429."`
- `phase_range = range(168, 431)`
- `aggregate_range = "range(168, 431)"`
- Add `stale_aggregate_range_430 = "".join(["range(168, ", "43", "0", ")"])` and include it in the stale tuple.
- Add `stale_aggregate_guard_430 = "".join(["range(168, ", "43", str(0), ")"])` and assert it is absent.
- Preserve stale split/direct guards for 429/428/427/426/425/424/423/422/421.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.
- Do not require the newest label exactly once in the test source; enforce single anchored constants and attention status semantics.

## Verification Gates

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-03-hermes-tavern-phase430-attention-status-sync-through-phase429 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase430-worker python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- If feasible with plugin autoload enabled: `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider`
- Static changed-path/protected-path guard over changed plus untracked files.
- Final-newline/trailing-whitespace guard.
- `git diff --check`

## Parent Handoff Boundary

S1 is non-final. Executor must leave `acceptance.md` absent, keep checklist acceptance state pending parent verification, avoid staging/commit/push, and hand back to parent/controller for verification and closeout.
