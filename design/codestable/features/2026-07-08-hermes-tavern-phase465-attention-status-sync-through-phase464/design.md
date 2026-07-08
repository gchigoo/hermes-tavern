---
doc_type: feature-design
feature: 2026-07-08-hermes-tavern-phase465-attention-status-sync-through-phase464
title: "Phase 465 attention/status sync through Phase 464"
status: approved
implementation_ready: true
date: "2026-07-08"
owner: company-boost
lane: company-boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 465, executor limited to status docs/tests plus non-final checklist handoff."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase465, company-boost]
---

# Phase 465 attention/status sync through Phase 464

## Scope

This bounded S1 handoff covers only the Phase 465 status-sync artifacts. The executor must keep work limited to the current-status source of truth, the focused status regression, and this Phase 465 feature `design.md` / `checklist.yaml`.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, build, cache, or service lifecycle changes.
- No root design, README, architecture, roadmap, requirements, compound docs, or later-phase work.
- No later-phase labels, guards, directories, or artifacts.
- No `acceptance.md` creation in S1.
- No staging, commit, push, stash, or parent-finalization claims.

## Allowed Files

Only these files may be edited or created for this handoff:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-08-hermes-tavern-phase465-attention-status-sync-through-phase464/design.md`
- `design/codestable/features/2026-07-08-hermes-tavern-phase465-attention-status-sync-through-phase464/checklist.yaml`

## Exact Status And Test Contract

### attention.md

- The single current-status line must start with `Current status (2026-06-18): All phases 1-465 accepted`.
- The status line must include `Phase 465 attention status sync through Phase 464` exactly once.
- Prior labels must remain intact.
- The status line must end exactly with `Phase 463 attention status sync through Phase 462, Phase 464 attention status sync through Phase 463, and Phase 465 attention status sync through Phase 464.`
- Placement must remain under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-465 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-464 accepted"`
- `STALE_PHASE_MARKER = "1-464"`
- `STALE_PHASE_MARKER_EN_DASH = "1–464"`
- Older stale guards for `1-463` and `1–463` must remain present.
- `REQUIRED_PHASE_LABELS` must include `Phase 465 attention status sync through Phase 464` after Phase 464.
- `FINAL_STATUS_SUFFIX = "Phase 463 attention status sync through Phase 462, Phase 464 attention status sync through Phase 463, and Phase 465 attention status sync through Phase 464."`
- `phase_range = range(168, 466)`
- `aggregate_range = "range(168, 466)"`
- Add split stale guard `stale_aggregate_range_465 = "".join(["range(168, ", "46", "5", ")"])`.
- Add split stale direct guard `stale_aggregate_guard_465 = "".join(["range(168, ", "46", str(5), ")"])`.
- Stale split/direct guards must reject the previous aggregate range and older direct ranges without embedding stale contiguous range literals that self-match in the test source.
- Anchored single-assignment guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX` must remain in place.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-08-hermes-tavern-phase465-attention-status-sync-through-phase464 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase465-executor python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static allowed-path/status/range/no-later-phase/no-acceptance guard over changed plus untracked files.
- `git diff --check`

## Parent Handoff

Parent verification is required after S1. Leave `acceptance.md` absent, keep checklist workflow and acceptance state pending parent verification, avoid commit/push activity, and hand back to the parent for final verification and any later acceptance or delivery steps.
