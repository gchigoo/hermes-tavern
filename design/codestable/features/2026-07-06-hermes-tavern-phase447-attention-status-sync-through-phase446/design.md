---
doc_type: feature-design
feature: 2026-07-06-hermes-tavern-phase447-attention-status-sync-through-phase446
title: "Phase 447 attention/status sync through Phase 446"
status: approved
implementation_ready: true
date: "2026-07-06"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "S1 status-sync only"
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase447, company-boost]
---

# Phase 447 attention/status sync through Phase 446

## Scope

- Bounded work only: sync `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` through accepted Phase 446.
- Create and maintain Phase 447 `design.md` and `checklist.yaml` only under `design/codestable/features/2026-07-06-hermes-tavern-phase447-attention-status-sync-through-phase446/`.
- Leave parent verification and acceptance closeout pending; no acceptance artifact is created in the S1 executor task.

## Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-06-hermes-tavern-phase447-attention-status-sync-through-phase446/design.md`
- `design/codestable/features/2026-07-06-hermes-tavern-phase447-attention-status-sync-through-phase446/checklist.yaml`

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache edits.
- No acceptance.md creation during S1, no later-phase paths, labels, tests, artifacts, or references, and no external state updates.
- No stage, commit, push, stash, dependency install, service lifecycle command, credential read, or credential mutation.
- No changes to Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP safety boundaries, minors/CSAM restrictions, or provider safety behavior.

## Exact Status Contract

### attention.md

- Replace the live prefix `Current status (2026-06-18): All phases 1-446 accepted` with `Current status (2026-06-18): All phases 1-447 accepted`.
- Preserve all existing labels and append exactly `Phase 447 attention status sync through Phase 446` immediately after the Phase 446 label.
- Keep the status bullet immediately after the adult-fiction non-negotiable bullet under `### 其他` and before `### Hermes Tavern 凭证约束`.
- End the status line exactly with `Phase 445 attention status sync through Phase 444, Phase 446 attention status sync through Phase 445, and Phase 447 attention status sync through Phase 446.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-447 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-446 accepted"`
- `STALE_PHASE_MARKER = "1-446"`
- `STALE_PHASE_MARKER_EN_DASH = "1–446"`
- Add `Phase 447 attention status sync through Phase 446` immediately after `Phase 446 attention status sync through Phase 445` in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 445 attention status sync through Phase 444, Phase 446 attention status sync through Phase 445, and Phase 447 attention status sync through Phase 446."`
- `phase_range = range(168, 448)`
- `aggregate_range = "range(168, 448)"`
- Add `stale_aggregate_range_447 = "".join(["range(168, ", "44", "7", ")"])` and include it in the stale-range tuple.
- Add `stale_aggregate_guard_447 = "".join(["range(168, ", "44", str(7), ")"])` and assert it is absent from the test source.
- Do not leave direct stale literal `range(168, 447)` as a live aggregate literal except through split construction; the live direct aggregate literal is `range(168, 448)`.
- Preserve existing stale guards, anchored assignment-count checks, section-placement guard, all-label guard, Phase 121-167 aggregate guard, and no-discovery-token guards.

## Static Guards

- Allowed dirty paths from `git diff --name-only`, `git diff --cached --name-only`, and `git ls-files --others --exclude-standard` must equal only the four allowed files.
- Phase 447 `acceptance.md` must remain absent by path; checklist must keep `acceptance_artifact: null` and `acceptance_md_present: false`.
- The attention line must have exactly one current-status bullet, the exact Phase 447 prefix/suffix, the new Phase 447 label exactly once, and no stale Phase 446 aggregate status in the current status line.
- The focused test constants, ranges, label list, anchored assignment counts, stale split range, direct stale guard, all-label guard, section placement, and no-discovery-token guards must remain intact.
- No later-phase path/status-label/artifact leakage, protected path changes, stage/commit/push, trailing whitespace, or missing final newline.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-06-hermes-tavern-phase447-attention-status-sync-through-phase446 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase447-executor python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`

## Parent Handoff

- Parent owns full verification, acceptance.md creation, and any commit/push decision.
- Executor leaves the repo dirty and uncommitted for parent verification.
