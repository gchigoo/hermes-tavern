---
doc_type: feature-design
feature: 2026-07-08-hermes-tavern-phase464-attention-status-sync-through-phase463
title: "Phase 464 attention/status sync through Phase 463"
status: approved
implementation_ready: true
date: "2026-07-08"
owner: company-boost
lane: company-boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 464, executor limited to status docs/tests plus non-final checklist handoff."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase464, company-boost]
---

# Phase 464 attention/status sync through Phase 463

## Scope

This bounded S1 handoff covers only the Phase 464 status-sync artifacts. The executor must keep work limited to the current-status source of truth, the focused status regression, and this Phase 464 feature `design.md` / `checklist.yaml`.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, build, cache, or service lifecycle changes.
- No root design, README, architecture, roadmap, requirements, compound docs, or later-phase work.
- No Phase 465 labels, guards, directories, or artifacts.
- No `acceptance.md` creation in S1.
- No staging, commit, push, stash, or parent-finalization claims.

## Allowed Files

Only these files may be edited or created for this handoff:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-08-hermes-tavern-phase464-attention-status-sync-through-phase463/design.md`
- `design/codestable/features/2026-07-08-hermes-tavern-phase464-attention-status-sync-through-phase463/checklist.yaml`

## Exact Status And Test Contract

### attention.md

- The single current-status line must start with `Current status (2026-06-18): All phases 1-464 accepted`.
- The status line must include `Phase 464 attention status sync through Phase 463` exactly once.
- Prior labels must remain intact.
- The status line must end exactly with `Phase 462 attention status sync through Phase 461, Phase 463 attention status sync through Phase 462, and Phase 464 attention status sync through Phase 463.`
- Placement must remain under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-464 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-463 accepted"`
- `STALE_PHASE_MARKER = "1-463"`
- `STALE_PHASE_MARKER_EN_DASH = "1–463"`
- Older stale guards for `1-462` and `1–462` must remain present.
- `REQUIRED_PHASE_LABELS` must include `Phase 464 attention status sync through Phase 463` after Phase 463.
- `FINAL_STATUS_SUFFIX = "Phase 462 attention status sync through Phase 461, Phase 463 attention status sync through Phase 462, and Phase 464 attention status sync through Phase 463."`
- `phase_range = range(168, 465)`
- `aggregate_range = "range(168, 465)"`
- Add split stale guard `stale_aggregate_range_464 = "".join(["range(168, ", "46", "4", ")"])`.
- Add split stale direct guard `stale_aggregate_guard_464 = "".join(["range(168, ", "46", str(4), ")"])`.
- Stale split/direct guards must reject the previous aggregate range and older direct ranges without embedding stale contiguous range literals that self-match in the test source.
- Anchored single-assignment guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX` must remain in place.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-08-hermes-tavern-phase464-attention-status-sync-through-phase463 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase464-executor python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static allowed-path/status/range/no-Phase-465/no-acceptance guard over changed plus untracked files.
- `git diff --check`

## Parent Handoff

Parent verification is required after S1. Leave `acceptance.md` absent, keep checklist workflow and acceptance state pending parent verification, avoid commit/push activity, and hand back to the parent for final verification and any later acceptance or delivery steps.
