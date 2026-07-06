---
doc_type: feature-design
feature: 2026-07-06-hermes-tavern-phase441-attention-status-sync-through-phase440
title: "Phase 441 attention/status sync through Phase 440"
status: approved
implementation_ready: true
date: "2026-07-06"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 441, executor limited to status docs/tests plus non-final checklist handoff."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase441, company-boost]
---

# Phase 441 attention/status sync through Phase 440

## Scope

- Bounded work only: sync `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` through accepted Phase 440.
- Create Phase 441 `design.md` and `checklist.yaml` only under `design/codestable/features/2026-07-06-hermes-tavern-phase441-attention-status-sync-through-phase440/`.
- Leave S2 parent verification and acceptance closeout pending; no acceptance artifact is created in the S1 executor task.

## Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-06-hermes-tavern-phase441-attention-status-sync-through-phase440/design.md`
- `design/codestable/features/2026-07-06-hermes-tavern-phase441-attention-status-sync-through-phase440/checklist.yaml`

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache edits.
- No acceptance.md creation during S1, no later-phase paths/labels/tests/artifacts, and no external state updates.
- No stage, commit, push, stash, dependency install, service lifecycle command, credential read, or credential mutation.
- No changes to Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP policy boundaries, minors/CSAM restrictions, or provider safety behavior.

## Exact Status Contract

### attention.md

- Replace the live prefix `Current status (2026-06-18): All phases 1-440 accepted` with `Current status (2026-06-18): All phases 1-441 accepted`.
- Preserve all existing special early labels, including Phase 121-167, plus every Phase 168-440 label already present.
- Append only `Phase 441 attention status sync through Phase 440` immediately after the Phase 440 label.
- Keep the status bullet immediately after the adult-fiction non-negotiable bullet under `### 其他` and before `### Hermes Tavern 凭证约束`.
- End the status line exactly with `Phase 439 attention status sync through Phase 438, Phase 440 attention status sync through Phase 439, and Phase 441 attention status sync through Phase 440.`
- Stale terminal status markers `1-440` and `1–440` must be absent from the current attention status line.

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-441 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-440 accepted"`
- `STALE_PHASE_MARKER = "1-440"`
- `STALE_PHASE_MARKER_EN_DASH = "1–440"`
- Add `Phase 441 attention status sync through Phase 440` after the Phase 440 entry in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 439 attention status sync through Phase 438, Phase 440 attention status sync through Phase 439, and Phase 441 attention status sync through Phase 440."`
- `phase_range = range(168, 442)`
- `aggregate_range = "range(168, 442)"`
- Add split-string stale guards for the old `range(168, 441)` aggregate without leaving a direct stale literal in the test source.
- Preserve stale guards for earlier ranges, anchored assignment-count checks, section-placement guard, all-label guard, Phase 121-167 aggregate guard, and no-discovery-token guards.
- Do not require newest label exactly once in the test source; it appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-06-hermes-tavern-phase441-attention-status-sync-through-phase440 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase441-s1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static guard over changed and untracked files: only the four allowed S1 files, no acceptance artifact, no later-phase artifacts/labels, final newline, and no trailing whitespace.
- `git diff --check`
- `python -m pytest -q -o 'addopts='` if feasible.

## Parent Handoff

- S1 remains non-final. Parent/controller owns verification closeout, any acceptance artifact creation, and any commit/push decision.
