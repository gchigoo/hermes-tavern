---
doc_type: feature-design
feature: 2026-07-04-hermes-tavern-phase437-attention-status-sync-through-phase436
title: "Phase 437 attention/status sync through Phase 436"
status: approved
implementation_ready: true
date: "2026-07-04"
owner: standard-lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 437 attention/status sync through accepted Phase 436; executor work is limited to status docs/tests plus non-final checklist handoff, with parent verification retaining acceptance authority."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase437, standard]
---

# Phase 437 attention/status sync through Phase 436

## Scope

- Bounded work only: sync `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` through accepted Phase 436.
- Create Phase 437 `design.md` and `checklist.yaml` only under `design/codestable/features/2026-07-04-hermes-tavern-phase437-attention-status-sync-through-phase436/`.
- Leave S2 parent verification and acceptance closeout pending; no acceptance artifact is created in the S1 executor task.

## Current Inputs

- `design/codestable/attention.md` currently has one live status bullet starting with `Current status (2026-06-18): All phases 1-436 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently has Phase 436 current/stale markers, `REQUIRED_PHASE_LABELS` through Phase 436, `FINAL_STATUS_SUFFIX` ending at Phase 436, and aggregate range `range(168, 437)`.
- The accepted Phase 436 feature artifact defers the next residual work to Phase 437 attention/status sync through Phase 436.

## Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-04-hermes-tavern-phase437-attention-status-sync-through-phase436/design.md`
- `design/codestable/features/2026-07-04-hermes-tavern-phase437-attention-status-sync-through-phase436/checklist.yaml`

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache edits.
- No acceptance.md creation during S1, no Phase 438 or later paths/labels/tests/artifacts, and no external state updates.
- No stage, commit, push, stash, dependency install, service lifecycle command, or credential mutation.
- No changes to Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP policy boundaries, minors/CSAM restrictions, or provider safety behavior.

## Exact Status Contract

### attention.md

- Replace the live prefix `Current status (2026-06-18): All phases 1-436 accepted` with `Current status (2026-06-18): All phases 1-437 accepted`.
- Preserve all existing special early labels, including Phase 121-167, plus every Phase 168-436 label already present.
- Append only `Phase 437 attention status sync through Phase 436` immediately after the Phase 436 label.
- Keep the status bullet immediately after the adult-fiction non-negotiable bullet under `### 其他` and before `### Hermes Tavern 凭证约束`.
- The newest label must appear exactly once in attention.
- End the status line exactly with `Phase 435 attention status sync through Phase 434, Phase 436 attention status sync through Phase 435, and Phase 437 attention status sync through Phase 436.`
- The stale live prefix `1-436` and en-dash variant `1–436` must be absent from the edited attention status line.

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-437 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-436 accepted"`
- `STALE_PHASE_MARKER = "1-436"`
- `STALE_PHASE_MARKER_EN_DASH = "1–436"`
- Add `Phase 437 attention status sync through Phase 436` after the Phase 436 entry in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 435 attention status sync through Phase 434, Phase 436 attention status sync through Phase 435, and Phase 437 attention status sync through Phase 436."`
- `phase_range = range(168, 438)`
- `aggregate_range = "range(168, 438)"`
- Add `stale_aggregate_range_437 = "".join(["range(168, ", "43", "7", ")"])` to the stale-range tuple and assert all stale ranges are absent from the test source.
- Add `stale_aggregate_guard_437 = "".join(["range(168, ", "43", str(7), ")"])` and assert it is absent while preserving existing 436/435/434/433/432/431/430/429 and earlier stale guards.
- Direct stale literal `range(168, 437)` must be absent from the live test source, while current `range(168, 438)` must be present.
- Preserve anchored assignment-count checks for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.
- Preserve section-placement, all-label, Phase 121-167 aggregate, split stale guard handling, and no-discovery-token guards.
- Do not impose global uniqueness for the newest label in the test source; it may appear in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Structure Health

This slice is intentionally static and narrow. No source modules or directories are structurally modified. The existing focused status test is long but purpose-built as a self-guarding status contract; splitting it would exceed the lane scope and risk unrelated churn. No micro-refactor is planned.

## Verification Gates

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-04-hermes-tavern-phase437-attention-status-sync-through-phase436 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase437-child python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static guard over changed/untracked paths for exact allowed paths only, no staged files, no acceptance.md during S1, no Phase 438+ files/live labels/accepted artifacts, current status/suffix/ranges/stale guards correct, every `REQUIRED_PHASE_LABELS` label present in attention, newest label exactly once in attention, direct stale live prefix absent from attention, direct stale literal `range(168, 437)` absent from test source while split stale guards may be present, live `range(168, 438)` present, final newline, no trailing whitespace, and current status section placement preserved.
- `git diff --check`
- If feasible: `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider`

## Parent Handoff Boundary

S1 remains non-final. Parent/controller owns S2 closeout, any acceptance artifact, and any commit/push decision. The S1 execution must leave uncommitted S1/S2-ready artifacts only.
