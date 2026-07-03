---
doc_type: feature-design
feature: 2026-07-03-hermes-tavern-phase434-attention-status-sync-through-phase433
title: "Phase 434 attention/status sync through Phase 433"
status: approved
implementation_ready: true
date: "2026-07-03"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 434 attention/status sync through accepted Phase 433; executor work is limited to status docs/tests plus non-final checklist handoff, with parent verification retaining acceptance authority."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase434, company-boost]
---

# Phase 434 attention/status sync through Phase 433

## Scope

- Bounded work only: sync `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` through accepted Phase 433.
- Create Phase 434 `design.md` and `checklist.yaml` only under `design/codestable/features/2026-07-03-hermes-tavern-phase434-attention-status-sync-through-phase433/`.
- Leave S2 parent verification and acceptance closeout pending; no acceptance artifact is created in this child-lane task.

## Current Inputs

- `design/codestable/attention.md` currently has one live status bullet starting with `Current status (2026-06-18): All phases 1-433 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently has Phase 433 current/stale markers, `REQUIRED_PHASE_LABELS` through Phase 433, `FINAL_STATUS_SUFFIX` ending at Phase 433, and aggregate range `range(168, 434)`.
- The accepted Phase 433 feature artifact defers the next residual work to Phase 434 attention/status sync through Phase 433.

## Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-03-hermes-tavern-phase434-attention-status-sync-through-phase433/design.md`
- `design/codestable/features/2026-07-03-hermes-tavern-phase434-attention-status-sync-through-phase433/checklist.yaml`

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache edits.
- No acceptance.md creation, no Phase 435 or later paths/labels/tests/artifacts, and no external state updates.
- No stage, commit, push, stash, dependency install, service lifecycle command, or credential mutation.
- No changes to Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP policy boundaries, minors/CSAM restrictions, or provider safety behavior.

## Exact Status Contract

### attention.md

- Replace the live prefix `Current status (2026-06-18): All phases 1-433 accepted` with `Current status (2026-06-18): All phases 1-434 accepted`.
- Preserve all existing special early labels plus every Phase 168-433 label already present.
- Append only `Phase 434 attention status sync through Phase 433`.
- Keep the status bullet immediately after the adult-fiction non-negotiable bullet under `### 其他` and before `### Hermes Tavern 凭证约束`.
- The newest label must appear exactly once in attention.
- End the status line exactly with `Phase 432 attention status sync through Phase 431, Phase 433 attention status sync through Phase 432, and Phase 434 attention status sync through Phase 433.`
- The stale live prefix `1-433` and en-dash variant `1–433` must be absent from the edited attention status line.

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-434 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-433 accepted"`
- `STALE_PHASE_MARKER = "1-433"`
- `STALE_PHASE_MARKER_EN_DASH = "1–433"`
- Add `Phase 434 attention status sync through Phase 433` after the Phase 433 entry in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 432 attention status sync through Phase 431, Phase 433 attention status sync through Phase 432, and Phase 434 attention status sync through Phase 433."`
- `phase_range = range(168, 435)`
- `aggregate_range = "range(168, 435)"`
- Add `stale_aggregate_range_434 = "".join(["range(168, ", "43", "4", ")"])` to the stale-range tuple and assert all stale ranges are absent from the test source.
- Add `stale_aggregate_guard_434 = "".join(["range(168, ", "43", str(4), ")"])` and assert it is absent while preserving existing 433/432/431/430/429 and earlier stale guards.
- Direct stale literal `range(168, 434)` must be absent from the live test source, while current `range(168, 435)` must be present.
- Preserve anchored assignment-count checks for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.
- Preserve section-placement, all-label, Phase 121-167 aggregate, split stale guard handling, and no-discovery-token guards.
- Do not impose global uniqueness for the newest label in the test source; it may appear in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Structure Health

This slice is intentionally static and narrow. No source modules or directories are structurally modified. The existing focused status test is long but purpose-built as a self-guarding status contract; splitting it would exceed the lane scope and risk unrelated churn.

## Verification Gates

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-03-hermes-tavern-phase434-attention-status-sync-through-phase433 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase434-child python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static guard over changed/untracked paths for exact allowed paths only, no staged files, no acceptance.md, no Phase 435+ files, current status/suffix/ranges/stale guards correct, every `REQUIRED_PHASE_LABELS` label present in attention, newest label exactly once in attention, direct stale live prefix absent from attention, direct stale literal `range(168, 434)` absent from test source while split stale guards may be present, live `range(168, 435)` present, final newline, and no trailing whitespace.
- `git diff --check`
- If feasible: `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider`

## Executor Prompt

Use the architect JSONL plan at `/tmp/hermes-tavern-companyboost-architect-phase434-20260703-163604.jsonl`. Execute only the four allowed files above. Advance attention/test to Phase 434 exactly as specified, keep the checklist non-final for parent verification, do not create `acceptance.md`, do not stage/commit/push, and stop after S1 handoff.

## Parent Handoff Boundary

S1 remains non-final. Parent/controller owns S2 closeout, any acceptance artifact, and any commit/push decision. This child-lane execution must leave uncommitted S1/S2-ready artifacts only.
