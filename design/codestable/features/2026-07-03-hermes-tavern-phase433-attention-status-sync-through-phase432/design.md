---
doc_type: feature-design
feature: 2026-07-03-hermes-tavern-phase433-attention-status-sync-through-phase432
title: "Phase 433 attention/status sync through Phase 432"
status: approved
implementation_ready: true
date: "2026-07-03"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 433 attention/status sync through accepted Phase 432; executor work is limited to status docs/tests plus non-final checklist handoff, with parent verification retaining acceptance authority."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase433, company-boost]
---

# Phase 433 attention/status sync through Phase 432

## Scope

- Bounded work only: sync `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` through accepted Phase 432.
- Create Phase 433 `design.md` and `checklist.yaml` only under `design/codestable/features/2026-07-03-hermes-tavern-phase433-attention-status-sync-through-phase432/`.
- Leave S2 parent verification and acceptance closeout pending; no acceptance artifact is created in this child-lane task.

## Current Inputs

- `design/codestable/attention.md` currently has one live status bullet starting with `Current status (2026-06-18): All phases 1-432 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently has Phase 432 current/stale markers, `REQUIRED_PHASE_LABELS` through Phase 432, `FINAL_STATUS_SUFFIX` ending at Phase 432, and aggregate range `range(168, 433)`.
- The accepted Phase 432 feature artifact defers the next residual work to Phase 433 attention/status sync through Phase 432.

## Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-03-hermes-tavern-phase433-attention-status-sync-through-phase432/design.md`
- `design/codestable/features/2026-07-03-hermes-tavern-phase433-attention-status-sync-through-phase432/checklist.yaml`

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache edits.
- No acceptance.md creation, no Phase 434 or later paths/labels/tests/artifacts, and no external state updates.
- No stage, commit, push, stash, dependency install, service lifecycle command, or credential mutation.
- No changes to Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP policy boundaries, minors/CSAM restrictions, or provider safety behavior.

## Exact Status Contract

### attention.md

- Replace the live prefix `Current status (2026-06-18): All phases 1-432 accepted` with `Current status (2026-06-18): All phases 1-433 accepted`.
- Preserve all existing special early labels plus every Phase 168-432 label already present.
- Append only `Phase 433 attention status sync through Phase 432`.
- Keep the status bullet immediately after the adult-fiction non-negotiable bullet under `### 其他` and before `### Hermes Tavern 凭证约束`.
- The newest label must appear exactly once in attention.
- End the status line exactly with `Phase 431 attention status sync through Phase 430, Phase 432 attention status sync through Phase 431, and Phase 433 attention status sync through Phase 432.`
- The stale live prefix `1-432` and en-dash variant `1–432` must be absent from the edited attention status line.

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-433 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-432 accepted"`
- `STALE_PHASE_MARKER = "1-432"`
- `STALE_PHASE_MARKER_EN_DASH = "1–432"`
- Add `Phase 433 attention status sync through Phase 432` after the Phase 432 entry in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 431 attention status sync through Phase 430, Phase 432 attention status sync through Phase 431, and Phase 433 attention status sync through Phase 432."`
- `phase_range = range(168, 434)`
- `aggregate_range = "range(168, 434)"`
- Add `stale_aggregate_range_433 = "".join(["range(168, ", "43", "3", ")"])` to the stale-range tuple and assert all stale ranges are absent from the test source.
- Add `stale_aggregate_guard_433 = "".join(["range(168, ", "43", str(3), ")"])` and assert it is absent while preserving existing 432/431/430/429 and earlier stale guards.
- Direct stale literal `range(168, 433)` must be absent from the live test source, while current `range(168, 434)` must be present.
- Preserve anchored assignment-count checks for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.
- Preserve section-placement, all-label, Phase 121-167 aggregate, split stale guard handling, and no-discovery-token guards.
- Do not impose global uniqueness for the newest label in the test source; it may appear in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Structure Health

This slice is intentionally static and narrow. No source modules or directories are structurally modified. The existing focused status test is long but purpose-built as a self-guarding status contract; splitting it would exceed the lane scope and risk unrelated churn. No micro-refactor is planned.

## Verification Gates

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-03-hermes-tavern-phase433-attention-status-sync-through-phase432 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase433-child python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static guard over changed/untracked paths for exact allowed paths only, no staged files, no acceptance.md, no Phase 434+ files, current status/suffix/ranges/stale guards correct, every `REQUIRED_PHASE_LABELS` label present in attention, newest label exactly once in attention, direct stale live prefix absent from attention, direct stale literal `range(168, 433)` absent from test source while split stale guards may be present, live `range(168, 434)` present, final newline, and no trailing whitespace.
- `git diff --check`
- If feasible: `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider`

## Executor Prompt

Use the architect JSONL plan at `/tmp/hermes-tavern-companyboost-architect-phase433-20260703-152025.jsonl`. Execute only the four allowed files above. Advance attention/test to Phase 433 exactly as specified, keep the checklist non-final for parent verification, do not create `acceptance.md`, do not stage/commit/push, and stop after S1 handoff.

## Parent Handoff Boundary

S1 remains non-final. Parent/controller owns S2 closeout, any acceptance artifact, and any commit/push decision. This child-lane execution must leave uncommitted S1/S2-ready artifacts only.
