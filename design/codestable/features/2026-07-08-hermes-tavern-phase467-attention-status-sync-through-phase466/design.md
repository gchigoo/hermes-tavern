---
doc_type: feature-design
feature: 2026-07-08-hermes-tavern-phase467-attention-status-sync-through-phase466
title: "Phase 467 attention/status sync through Phase 466"
status: approved
implementation_ready: true
date: "2026-07-08"
owner: company-boost
lane: company-boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 467, executor limited to status docs/tests plus non-final parent-verification handoff."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase467, company-boost]
---

# Phase 467 attention/status sync through Phase 466

## Scope

This bounded S1 handoff covers only the Phase 467 status-sync artifacts. The executor must keep work limited to the current-status source of truth, the focused status regression, and this Phase 467 feature `design.md` / `checklist.yaml`.

## Lifecycle

This is S1 only. Parent verification remains required after executor/controller gates. Do not create `acceptance.md`; keep the checklist non-final with `workflow_status`, `acceptance_state`, and parent-verification fields pending.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, build, cache, or service lifecycle changes.
- No root design, README, architecture, roadmap, requirements, compound docs, or any out-of-scope work.
- No out-of-scope labels, guards, directories, or artifacts.
- No `acceptance.md` creation in S1.
- No staging, commit, push, stash, or parent-finalization claims.

## Allowed Files

Only these files may be edited or created for this handoff:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-08-hermes-tavern-phase467-attention-status-sync-through-phase466/design.md`
- `design/codestable/features/2026-07-08-hermes-tavern-phase467-attention-status-sync-through-phase466/checklist.yaml`

## Safety And Compatibility Boundaries

Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP compatibility, provider safety boundaries, credential handling, gateway behavior, and service lifecycle behavior are unchanged. Do not introduce minors/CSAM behavior or provider-safety-bypass work.

## Exact Status And Test Contract

### attention.md

- Advance the single current-status line to start with `Current status (2026-06-18): All phases 1-467 accepted`.
- Append exactly one label: `Phase 467 attention status sync through Phase 466`.
- Preserve all prior required labels, including the Phase 121-167 aggregate and all Phase 168-466 labels.
- Preserve placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix must be exactly: `Phase 465 attention status sync through Phase 464, Phase 466 attention status sync through Phase 465, and Phase 467 attention status sync through Phase 466.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-467 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-466 accepted"`
- `STALE_PHASE_MARKER = "1-466"`
- `STALE_PHASE_MARKER_EN_DASH = "1–466"`
- `OLDER_STALE_PHASE_MARKER = "1-465"`
- `OLDER_STALE_PHASE_MARKER_EN_DASH = "1–465"`
- Append `Phase 467 attention status sync through Phase 466` to `REQUIRED_PHASE_LABELS` after Phase 466.
- `FINAL_STATUS_SUFFIX = "Phase 465 attention status sync through Phase 464, Phase 466 attention status sync through Phase 465, and Phase 467 attention status sync through Phase 466."`
- `phase_range = range(168, 468)`
- `aggregate_range = "range(168, 468)"`
- Add `stale_aggregate_range_467 = "".join(["range(168, ", "46", "7", ")"])`.
- Add `stale_aggregate_guard_467 = "".join(["range(168, ", "46", str(7), ")"])`.
- Include both new stale variables in the existing tuple/assertion checks; exact tuple order is not required.
- Preserve anchored assignment-count checks, section-placement guard, all-label guard, Phase 121-167 guard, no-discovery-token guards, and existing stale guards.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-08-hermes-tavern-phase467-attention-status-sync-through-phase466 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static allowed-path/status/range/newline/whitespace/no-acceptance/no-out-of-scope-artifact guard over `/opt/homebrew/bin/git diff --name-only`, `/opt/homebrew/bin/git diff --cached --name-only`, and `/opt/homebrew/bin/git ls-files --others --exclude-standard`.
- `/opt/homebrew/bin/git diff --check`
- Full pytest when feasible: `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`

## Parent Handoff

After S1, leave the tree dirty only in the allowed files, leave `acceptance.md` absent, keep checklist lifecycle pending parent verification, avoid commit/push activity, and hand back for parent closeout.
