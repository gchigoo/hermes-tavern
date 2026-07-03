---
doc_type: feature-design
feature: 2026-07-03-hermes-tavern-phase431-attention-status-sync-through-phase430
title: "Phase 431 attention/status sync through Phase 430"
status: approved
implementation_ready: true
date: "2026-07-03"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 431 attention/status sync through accepted Phase 430; executor work is limited to status docs/tests plus non-final checklist handoff, with parent verification retaining acceptance authority."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase431, company-boost]
---

# Phase 431 attention/status sync through Phase 430

## Scope

- Bounded work only: sync `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` through accepted Phase 430.
- Create Phase 431 `design.md` and `checklist.yaml` only under `design/codestable/features/2026-07-03-hermes-tavern-phase431-attention-status-sync-through-phase430/`.
- Leave S2 parent verification and acceptance closeout pending; no acceptance artifact is created in this child-lane task.

## Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-03-hermes-tavern-phase431-attention-status-sync-through-phase430/design.md`
- `design/codestable/features/2026-07-03-hermes-tavern-phase431-attention-status-sync-through-phase430/checklist.yaml`

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache edits.
- No acceptance.md creation, no Phase 432 or later paths/labels/tests/artifacts, and no external state updates.
- No stage, commit, push, stash, dependency install, service lifecycle command, or credential mutation.

## Exact Status Contract

### attention.md

- Replace the stale live prefix `Current status (2026-06-18): All phases 1-430 accepted` with `Current status (2026-06-18): All phases 1-431 accepted`.
- Preserve all existing special early labels plus every Phase 168-430 label already present.
- Append only `Phase 431 attention status sync through Phase 430`.
- Keep the status bullet immediately after the adult-fiction non-negotiable bullet under `### 其他` and before `### Hermes Tavern 凭证约束`.
- The newest label must appear exactly once in attention.
- End the status line exactly with `Phase 429 attention status sync through Phase 428, Phase 430 attention status sync through Phase 429, and Phase 431 attention status sync through Phase 430.`
- The stale live prefix `1-430` must be absent from the edited attention status line.

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-431 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-430 accepted"`
- `STALE_PHASE_MARKER = "1-430"`
- `STALE_PHASE_MARKER_EN_DASH = "1–430"`
- Add `Phase 431 attention status sync through Phase 430` after the Phase 430 entry in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 429 attention status sync through Phase 428, Phase 430 attention status sync through Phase 429, and Phase 431 attention status sync through Phase 430."`
- `phase_range = range(168, 432)`
- `aggregate_range = "range(168, 432)"`
- Add `stale_aggregate_range_431 = "".join(["range(168, ", "43", "1", ")"])` to the stale-range tuple and assert all stale ranges are absent from the test source.
- Add `stale_aggregate_guard_431 = "".join(["range(168, ", "43", str(1), ")"])` and assert it is absent while preserving the existing 430/429/etc. stale guards.
- Direct stale literal `range(168, 431)` must be absent from the live test source, while current `range(168, 432)` must be present.
- Preserve anchored assignment-count checks for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.
- Do not impose global uniqueness for the newest label in the test source; it may appear in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Verification Gates

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-03-hermes-tavern-phase431-attention-status-sync-through-phase430 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase431-child python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static guard over changed/untracked paths for exact allowed paths only, no staged files, no acceptance.md, no Phase 432+ files, current status/suffix/ranges/stale guards correct, every `REQUIRED_PHASE_LABELS` label present in attention, newest label exactly once in attention, direct stale live prefix absent from attention, direct stale literal `range(168, 431)` absent from test source while split stale guards may be present, live `range(168, 432)` present, final newline, and no trailing whitespace.
- `git diff --check`
- If feasible: `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider`

## Parent Handoff Boundary

S1 remains non-final. Parent/controller owns S2 closeout, any acceptance artifact, and any commit/push decision. This child-lane execution must leave uncommitted S1/S2-ready artifacts only.
