---
doc_type: feature-design
feature: 2026-07-07-hermes-tavern-phase450-attention-status-sync-through-phase449
title: "Phase 450 attention/status sync through Phase 449"
status: approved
implementation_ready: true
date: "2026-07-07"
owner: standard
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "S1 status-sync only"
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase450, standard]
---

# Phase 450 attention/status sync through Phase 449

## Scope

- Bounded work only: sync `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` through accepted Phase 449.
- Create and maintain Phase 450 `design.md` and `checklist.yaml` only under `design/codestable/features/2026-07-07-hermes-tavern-phase450-attention-status-sync-through-phase449/`.
- Leave parent verification and acceptance closeout pending; no acceptance artifact is created in the S1 executor task.

## Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-07-hermes-tavern-phase450-attention-status-sync-through-phase449/design.md`
- `design/codestable/features/2026-07-07-hermes-tavern-phase450-attention-status-sync-through-phase449/checklist.yaml`

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache edits.
- No acceptance.md creation during S1, no later-phase paths, labels, tests, artifacts, or references, and no external state updates.
- No stage, commit, push, stash, dependency install, service lifecycle command, credential read, or credential mutation.
- No changes to Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP safety boundaries, minors/CSAM restrictions, or provider safety behavior.

## Exact Status Contract

### attention.md

- Replace the live prefix `Current status (2026-06-18): All phases 1-449 accepted` with `Current status (2026-06-18): All phases 1-450 accepted`.
- Preserve all existing labels and append exactly `Phase 450 attention status sync through Phase 449` immediately after the Phase 449 label.
- Keep the status bullet immediately after the adult-fiction non-negotiable bullet under `### 其他` and before `### Hermes Tavern 凭证约束`.
- End the status line exactly with `Phase 448 attention status sync through Phase 447, Phase 449 attention status sync through Phase 448, and Phase 450 attention status sync through Phase 449.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-450 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-449 accepted"`
- `STALE_PHASE_MARKER = "1-449"`
- `STALE_PHASE_MARKER_EN_DASH = "1–449"`
- Add `Phase 450 attention status sync through Phase 449` immediately after `Phase 449 attention status sync through Phase 448` in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 448 attention status sync through Phase 447, Phase 449 attention status sync through Phase 448, and Phase 450 attention status sync through Phase 449."`
- `phase_range = range(168, 451)`
- `aggregate_range = "range(168, 451)"`
- Add `stale_aggregate_range_450 = "".join(["range(168, ", "45", "0", ")"])` and include it in the stale-range tuple.
- Add `stale_aggregate_guard_450 = "".join(["range(168, ", "45", str(0), ")"])` and assert it is absent from the test source.
- Do not leave direct stale literal `range(168, 450)` as a live aggregate literal except through split construction; the live direct aggregate literal is `range(168, 451)`.
- Preserve existing stale guards, anchored assignment-count checks, section-placement guard, all-label guard, Phase 121-167 aggregate guard, and no-discovery-token guards.

## Static Guards

- Allowed dirty paths from `git diff --name-only`, `git diff --cached --name-only`, and `git ls-files --others --exclude-standard` must equal only the four allowed files.
- Phase 450 `acceptance.md` must remain absent by path; checklist must keep `acceptance_artifact: null` and `acceptance_md_present: false`.
- The attention line must have exactly one current-status bullet, the exact Phase 450 prefix/suffix, the new Phase 450 label exactly once, and no stale Phase 449 aggregate status in the current status line.
- The focused test constants, ranges, label list, anchored assignment counts, stale split range, direct stale guard, all-label guard, section placement, Phase 121-167 aggregate guard, and no-discovery-token guards must remain intact.
- No later-phase path/status-label/artifact leakage, protected path changes, stage/commit/push, trailing whitespace, or missing final newline.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-07-hermes-tavern-phase450-attention-status-sync-through-phase449 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase450-executor python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`

## Parent Handoff

- Parent owns full verification, acceptance.md creation, checklist final-status updates, and any commit/push decision.
- Executor leaves the repo dirty and uncommitted for parent verification.
