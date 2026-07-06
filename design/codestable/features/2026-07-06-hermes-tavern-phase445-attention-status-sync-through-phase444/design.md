---
doc_type: feature-design
feature: 2026-07-06-hermes-tavern-phase445-attention-status-sync-through-phase444
title: "Phase 445 attention/status sync through Phase 444"
status: approved
implementation_ready: true
date: "2026-07-06"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "S1 status-sync only"
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase445, company-boost]
---

# Phase 445 attention/status sync through Phase 444

## Scope

- Bounded work only: sync `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` through accepted Phase 444.
- Create and maintain Phase 445 `design.md` and `checklist.yaml` only under `design/codestable/features/2026-07-06-hermes-tavern-phase445-attention-status-sync-through-phase444/`.
- Leave parent verification and acceptance closeout pending; no acceptance artifact is created in the S1 executor task.

## Allowed Files

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-06-hermes-tavern-phase445-attention-status-sync-through-phase444/design.md`
- `design/codestable/features/2026-07-06-hermes-tavern-phase445-attention-status-sync-through-phase444/checklist.yaml`

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, architecture, roadmap, requirements, compound, build, or cache edits.
- No acceptance.md creation during S1, no Phase 446+ paths, labels, tests, artifacts, or references, and no external state updates.
- No stage, commit, push, stash, dependency install, service lifecycle command, credential read, or credential mutation.
- No changes to Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP safety boundaries, minors/CSAM restrictions, or provider safety behavior.

## Exact Status Contract

### attention.md

- Replace the live prefix `Current status (2026-06-18): All phases 1-444 accepted` with `Current status (2026-06-18): All phases 1-445 accepted`.
- Preserve all existing labels and append exactly `Phase 445 attention status sync through Phase 444` immediately after the Phase 444 label.
- Keep the status bullet immediately after the adult-fiction non-negotiable bullet under `### 其他` and before `### Hermes Tavern 凭证约束`.
- End the status line exactly with `Phase 443 attention status sync through Phase 442, Phase 444 attention status sync through Phase 443, and Phase 445 attention status sync through Phase 444.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-445 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-444 accepted"`
- `STALE_PHASE_MARKER = "1-444"`
- `STALE_PHASE_MARKER_EN_DASH = "1–444"`
- Add `Phase 445 attention status sync through Phase 444` immediately after `Phase 444 attention status sync through Phase 443` in `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 443 attention status sync through Phase 442, Phase 444 attention status sync through Phase 443, and Phase 445 attention status sync through Phase 444."`
- `phase_range = range(168, 446)`
- `aggregate_range = "range(168, 446)"`
- Add `stale_aggregate_range_445 = "".join(["range(168, ", "44", "5", ")"])` and include it in the stale-range tuple.
- Add `stale_aggregate_guard_445 = "".join(["range(168, ", "44", str(5), ")"])` and assert it is absent from the test source.
- Preserve existing stale guards, anchored assignment-count checks, section-placement guard, all-label guard, Phase 121-167 aggregate guard, and no-discovery-token guards.
- Do not leave direct stale literal `range(168, 445)` as a live aggregate literal except via split construction; the live direct aggregate literal is `range(168, 446)`.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-06-hermes-tavern-phase445-attention-status-sync-through-phase444 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase445-executor python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`

## Parent Handoff

- Parent owns full verification, acceptance.md creation, and any commit/push decision.
- Executor leaves the repo dirty and uncommitted for parent verification.
