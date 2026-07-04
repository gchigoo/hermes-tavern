---
doc_type: feature-design
feature: 2026-07-04-hermes-tavern-phase439-attention-status-sync-through-phase438
title: "Phase 439 attention/status sync through Phase 438"
status: approved
implementation_ready: true
date: "2026-07-04"
owner: standard-lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 439, executor limited to status docs/tests plus non-final checklist handoff."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase439, standard]
---

# Phase 439 attention/status sync through Phase 438

## Scope

- Bounded work only: sync `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` through accepted Phase 438.
- Create Phase 439 `design.md` and `checklist.yaml` only under `design/codestable/features/2026-07-04-hermes-tavern-phase439-attention-status-sync-through-phase438/`.
- Leave S2 parent verification and acceptance closeout pending; no acceptance artifact is created in the S1 executor task.

## Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-04-hermes-tavern-phase439-attention-status-sync-through-phase438/design.md`
- `design/codestable/features/2026-07-04-hermes-tavern-phase439-attention-status-sync-through-phase438/checklist.yaml`

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache edits.
- No acceptance.md creation during S1, no Phase 440 or later paths/labels/tests/artifacts, and no external state updates.
- No stage, commit, push, stash, dependency install, service lifecycle command, credential read, or credential mutation.
- No changes to Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP policy boundaries, minors/CSAM restrictions, or provider safety behavior.

## Exact Status Contract

### attention.md

- Replace the live prefix `Current status (2026-06-18): All phases 1-438 accepted` with `Current status (2026-06-18): All phases 1-439 accepted`.
- Preserve all existing special early labels, including Phase 121-167, plus every Phase 168-438 label already present.
- Append only `Phase 439 attention status sync through Phase 438` immediately after the Phase 438 label.
- Keep the status bullet immediately after the adult-fiction non-negotiable bullet under `### 其他` and before `### Hermes Tavern 凭证约束`.
- End the status line exactly with `Phase 437 attention status sync through Phase 436, Phase 438 attention status sync through Phase 437, and Phase 439 attention status sync through Phase 438.`
- Stale terminal status/ranges `1-438` and `1–438` must be absent from the current attention status line.

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-439 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-438 accepted"`
- `STALE_PHASE_MARKER = "1-438"`
- `STALE_PHASE_MARKER_EN_DASH = "1–438"`
- Add `Phase 439 attention status sync through Phase 438` after the Phase 438 entry in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 437 attention status sync through Phase 436, Phase 438 attention status sync through Phase 437, and Phase 439 attention status sync through Phase 438."`
- `phase_range = range(168, 440)`
- `aggregate_range = "range(168, 440)"`
- Add `stale_aggregate_range_439 = "".join(["range(168, ", "43", "9", ")"])` to the stale-range absence tuple while preserving existing `stale_aggregate_range_438` and earlier.
- Add `stale_aggregate_guard_439 = "".join(["range(168, ", "43", str(9), ")"])` and assert it is absent while preserving existing `stale_aggregate_guard_438` and earlier.
- Direct stale contiguous literal `range(168, 439)` must be absent from the live test source except split or constructed stale guards, while current `range(168, 440)` must be present.
- Preserve anchored assignment-count checks, section-placement, all-label, Phase 121-167 aggregate, split stale guard handling, and no-discovery-token guards.
- Do not require newest label exactly once in the test source; it appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-04-hermes-tavern-phase439-attention-status-sync-through-phase438 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase439-child python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- `git diff --check`

## Parent Handoff

- S1 remains non-final. Parent/controller owns verification closeout, any acceptance artifact creation, and any commit/push decision.
