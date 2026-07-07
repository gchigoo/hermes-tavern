---
doc_type: feature-design
feature: 2026-07-07-hermes-tavern-phase461-attention-status-sync-through-phase460
title: "Phase 461 attention/status sync through Phase 460"
status: approved
implementation_ready: true
date: "2026-07-07"
owner: company-boost
lane: company-boost
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase461, company-boost]
---

# Phase 461 attention/status sync through Phase 460

## Scope

This bounded S1 handoff covers only the Phase 461 status-sync artifacts. The executor must keep the work limited to the current-status source of truth, the focused status regression, and the new Phase 461 feature `design.md` / `checklist.yaml`.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, build, cache, or service lifecycle changes.
- No root design, README, architecture, roadmap, requirements, compound docs, or Phase 462+ work.
- No `acceptance.md` creation in S1.
- No staging, commit, push, stash, or parent-finalization claims.

## Allowed Files

Only these files may be edited or created for this handoff:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-07-hermes-tavern-phase461-attention-status-sync-through-phase460/design.md`
- `design/codestable/features/2026-07-07-hermes-tavern-phase461-attention-status-sync-through-phase460/checklist.yaml`

## Exact Status And Test Contract

### attention.md

- The single current-status line must start with `Current status (2026-06-18): All phases 1-461 accepted`.
- The status line must include `Phase 461 attention status sync through Phase 460`.
- Prior labels must remain intact.
- The status line must end exactly with `Phase 459 attention status sync through Phase 458, Phase 460 attention status sync through Phase 459, and Phase 461 attention status sync through Phase 460.`
- Placement must remain under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-461 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-460 accepted"`
- `STALE_PHASE_MARKER = "1-460"`
- `STALE_PHASE_MARKER_EN_DASH = "1–460"`
- Older stale guards for `1-459` and `1–459` must remain present.
- `REQUIRED_PHASE_LABELS` must include `Phase 461 attention status sync through Phase 460` after Phase 460.
- `FINAL_STATUS_SUFFIX = "Phase 459 attention status sync through Phase 458, Phase 460 attention status sync through Phase 459, and Phase 461 attention status sync through Phase 460."`
- `phase_range = range(168, 462)`
- `aggregate_range = "range(168, 462)"`
- Stale split/direct guards must reject the stale contiguous prior range for Phase 460 while preserving earlier stale direct-range guards without embedding a raw contiguous `range(168, 461)` self-match in the test source.
- Anchored single-assignment guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX` must remain in place.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-07-hermes-tavern-phase461-attention-status-sync-through-phase460 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase461-executor python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`

## Parent Handoff

Parent verification is required after S1. Leave `acceptance.md` absent, keep checklist workflow and acceptance state pending parent verification, avoid commit/push activity, and hand back to the parent for final verification and any later acceptance or delivery steps.
