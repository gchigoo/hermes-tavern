---
doc_type: feature-design
feature: 2026-07-06-hermes-tavern-phase440-attention-status-sync-through-phase439
title: "Phase 440 attention/status sync through Phase 439"
status: approved
implementation_ready: true
date: "2026-07-06"
owner: standard-lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 440, executor limited to status docs/tests plus non-final checklist handoff."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase440, standard]
---

# Phase 440 attention/status sync through Phase 439

## Scope

- Bounded work only: sync `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` through accepted Phase 439.
- Create Phase 440 `design.md` and `checklist.yaml` only under `design/codestable/features/2026-07-06-hermes-tavern-phase440-attention-status-sync-through-phase439/`.
- Leave S2 parent verification and acceptance closeout pending; no acceptance artifact is created in the S1 executor task.

## Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-06-hermes-tavern-phase440-attention-status-sync-through-phase439/design.md`
- `design/codestable/features/2026-07-06-hermes-tavern-phase440-attention-status-sync-through-phase439/checklist.yaml`

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache edits.
- No acceptance.md creation during S1, no later-phase paths/labels/tests/artifacts, and no external state updates.
- No stage, commit, push, stash, dependency install, service lifecycle command, credential read, or credential mutation.
- No changes to Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP policy boundaries, minors/CSAM restrictions, or provider safety behavior.

## Exact Status Contract

### attention.md

- Replace the live prefix `Current status (2026-06-18): All phases 1-439 accepted` with `Current status (2026-06-18): All phases 1-440 accepted`.
- Preserve all existing special early labels, including Phase 121-167, plus every Phase 168-439 label already present.
- Append only `Phase 440 attention status sync through Phase 439` immediately after the Phase 439 label.
- Keep the status bullet immediately after the adult-fiction non-negotiable bullet under `### 其他` and before `### Hermes Tavern 凭证约束`.
- End the status line exactly with `Phase 438 attention status sync through Phase 437, Phase 439 attention status sync through Phase 438, and Phase 440 attention status sync through Phase 439.`
- Stale terminal status/ranges `1-439` and `1–439` must be absent from the current attention status line.

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-440 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-439 accepted"`
- `STALE_PHASE_MARKER = "1-439"`
- `STALE_PHASE_MARKER_EN_DASH = "1–439"`
- Add `Phase 440 attention status sync through Phase 439` after the Phase 439 entry in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 438 attention status sync through Phase 437, Phase 439 attention status sync through Phase 438, and Phase 440 attention status sync through Phase 439."`
- `phase_range = range(168, 441)`
- `aggregate_range = "range(168, 441)"`
- Add split-string stale guards for the old `range(168, 440)` aggregate without leaving a direct stale literal in the test source.
- Preserve stale guards for earlier ranges, anchored assignment-count checks, section-placement guard, all-label guard, Phase 121-167 aggregate guard, and no-discovery-token guards.
- Do not require newest label exactly once in the test source; it appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Verification

- `python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts='`
- `python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-06-hermes-tavern-phase440-attention-status-sync-through-phase439 --require doc_type --require feature --require status`
- `python -m pytest -q -o 'addopts='` if feasible, with plugin autoload enabled.
- `git diff --check`
- Static guard over changed and untracked files: only the four allowed S1 files, no acceptance artifact, no later-phase artifacts/labels, final newline, and no trailing whitespace.

## Parent Handoff

- S1 remains non-final. Parent/controller owns verification closeout, any acceptance artifact creation, and any commit/push decision.
