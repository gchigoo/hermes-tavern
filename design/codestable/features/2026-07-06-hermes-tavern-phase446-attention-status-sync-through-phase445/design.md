---
doc_type: feature-design
feature: 2026-07-06-hermes-tavern-phase446-attention-status-sync-through-phase445
title: "Phase 446 attention/status sync through Phase 445"
status: approved
implementation_ready: true
date: "2026-07-06"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "S1 status-sync only"
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase446, company-boost]
---

# Phase 446 attention/status sync through Phase 445

## Scope

- Bounded work only: sync `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` through accepted Phase 445.
- Create and maintain Phase 446 `design.md` and `checklist.yaml` only under `design/codestable/features/2026-07-06-hermes-tavern-phase446-attention-status-sync-through-phase445/`.
- Leave parent verification and acceptance closeout pending; no acceptance artifact is created in the S1 executor task.

## Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-06-hermes-tavern-phase446-attention-status-sync-through-phase445/design.md`
- `design/codestable/features/2026-07-06-hermes-tavern-phase446-attention-status-sync-through-phase445/checklist.yaml`

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache edits.
- No acceptance.md creation during S1, no later-phase paths, labels, tests, artifacts, or references, and no external state updates.
- No stage, commit, push, stash, dependency install, service lifecycle command, credential read, or credential mutation.
- No changes to Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP safety boundaries, minors/CSAM restrictions, or provider safety behavior.

## Exact Status Contract

### attention.md

- Replace the live prefix `Current status (2026-06-18): All phases 1-445 accepted` with `Current status (2026-06-18): All phases 1-446 accepted`.
- Preserve all existing labels and append exactly `Phase 446 attention status sync through Phase 445` immediately after the Phase 445 label.
- Keep the status bullet immediately after the adult-fiction non-negotiable bullet under `### 其他` and before `### Hermes Tavern 凭证约束`.
- End the status line exactly with `Phase 444 attention status sync through Phase 443, Phase 445 attention status sync through Phase 444, and Phase 446 attention status sync through Phase 445.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-446 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-445 accepted"`
- `STALE_PHASE_MARKER = "1-445"`
- `STALE_PHASE_MARKER_EN_DASH = "1–445"`
- Add `Phase 446 attention status sync through Phase 445` immediately after `Phase 445 attention status sync through Phase 444` in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 444 attention status sync through Phase 443, Phase 445 attention status sync through Phase 444, and Phase 446 attention status sync through Phase 445."`
- `phase_range = range(168, 447)`
- `aggregate_range = "range(168, 447)"`
- Add `stale_aggregate_range_446 = "".join(["range(168, ", "44", "6", ")"])` and include it in the stale-range tuple.
- Add `stale_aggregate_guard_446 = "".join(["range(168, ", "44", str(6), ")"])` and assert it is absent from the test source.
- Do not leave direct stale literal `range(168, 446)` as a live aggregate literal except through split construction; the live direct aggregate literal is `range(168, 447)`.
- Preserve existing stale guards, anchored assignment-count checks, section-placement guard, all-label guard, Phase 121-167 aggregate guard, and no-discovery-token guards.

## Static Guards

- Allowed dirty paths from `git diff --name-only`, `git diff --cached --name-only`, and `git ls-files --others --exclude-standard` must equal only the four allowed files.
- Phase 446 `acceptance.md` must remain absent by path; checklist must keep `acceptance_artifact: null` and `acceptance_md_present: false`.
- The attention line must have exactly one current-status bullet, the exact Phase 446 prefix/suffix, the new Phase 446 label exactly once, and no stale Phase 445 aggregate status in the current status line.
- The focused test constants, ranges, label list, anchored assignment counts, stale split range, direct stale guard, all-label guard, section placement, and no-discovery-token guards must remain intact.
- No later-phase path/status-label/artifact leakage, protected path changes, stage/commit/push, trailing whitespace, or missing final newline.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-06-hermes-tavern-phase446-attention-status-sync-through-phase445 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase446-executor python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `python /tmp/hermes-tavern-phase446-static-guard.py`
- `git diff --check`

## Parent Handoff

- Parent owns full verification, acceptance.md creation, and any commit/push decision.
- Executor leaves the repo dirty and uncommitted for parent verification.
