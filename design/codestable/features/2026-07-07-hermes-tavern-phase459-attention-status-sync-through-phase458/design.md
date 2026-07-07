---
doc_type: feature-design
feature: 2026-07-07-hermes-tavern-phase459-attention-status-sync-through-phase458
title: "Phase 459 attention/status sync through Phase 458"
status: approved
implementation_ready: true
date: "2026-07-07"
owner: company-boost
lane: company-boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 459, executor limited to status docs/tests plus non-final checklist handoff."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase459, company-boost]
---

# Phase 459 attention/status sync through Phase 458

## Scope

- Bounded work only: sync `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` through accepted Phase 458.
- Create and maintain Phase 459 `design.md` and `checklist.yaml` only under `design/codestable/features/2026-07-07-hermes-tavern-phase459-attention-status-sync-through-phase458/`.
- Leave S2 parent verification and acceptance closeout pending; no acceptance artifact is created in the S1 executor task.

## Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-07-hermes-tavern-phase459-attention-status-sync-through-phase458/design.md`
- `design/codestable/features/2026-07-07-hermes-tavern-phase459-attention-status-sync-through-phase458/checklist.yaml`

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache edits.
- No acceptance.md creation during S1, no later-phase paths/labels/tests/artifacts, and no external state updates.
- No stage, commit, push, stash, dependency install, service lifecycle command, credential read, or credential mutation.
- No changes to Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP policy boundaries, minors/CSAM restrictions, or provider safety behavior.

## Exact Status Contract

### attention.md

- Replace the live prefix `Current status (2026-06-18): All phases 1-458 accepted` with `Current status (2026-06-18): All phases 1-459 accepted`.
- Preserve all existing special early labels, including Phase 121-167, plus every Phase 168-458 label already present.
- Preserve `Phase 458 attention status sync through Phase 457` exactly once in the attention status line.
- Append only `Phase 459 attention status sync through Phase 458` immediately after the Phase 458 label.
- Keep the status bullet immediately after the adult-fiction non-negotiable bullet under `### 其他` and before `### Hermes Tavern 凭证约束`.
- End the status line exactly with `Phase 457 attention status sync through Phase 456, Phase 458 attention status sync through Phase 457, and Phase 459 attention status sync through Phase 458.`
- Stale terminal status markers `1-458` and `1–458` must be absent from the current attention status line.

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-459 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-458 accepted"`
- `STALE_PHASE_MARKER = "1-458"`
- `STALE_PHASE_MARKER_EN_DASH = "1–458"`
- Add `Phase 459 attention status sync through Phase 458` after the Phase 458 entry in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 457 attention status sync through Phase 456, Phase 458 attention status sync through Phase 457, and Phase 459 attention status sync through Phase 458."`
- `phase_range = range(168, 460)`
- `aggregate_range = "range(168, 460)"`
- Add split-string stale guards for the old `range(168, 459)` aggregate without leaving a direct stale literal in the test source.
- Preserve stale guards for earlier ranges, anchored assignment-count checks, section-placement guard, all-label guard, Phase 121-167 aggregate guard, and no-discovery-token guards.
- Do not require newest label exactly once in the test source; it appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-07-hermes-tavern-phase459-attention-status-sync-through-phase458 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase459-executor python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`

## Review Checklist

- Only the four S1 allowed paths are dirty.
- No Phase 459 `acceptance.md` exists.
- The attention line has exactly one `Phase 458 attention status sync through Phase 457` label and exactly one `Phase 459 attention status sync through Phase 458` label.
- `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX` are each assigned exactly once by anchored regex.
- The focused test rejects stale terminal status/ranges from Phase 458 while allowing valid internal aggregate ranges.

## Parent Handoff

- S1 remains non-final. Parent/controller owns verification closeout, any acceptance artifact creation, and any commit/push decision.
