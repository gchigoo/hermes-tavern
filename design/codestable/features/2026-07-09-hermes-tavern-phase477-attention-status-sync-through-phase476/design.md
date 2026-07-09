---
doc_type: feature-design
feature: 2026-07-09-hermes-tavern-phase477-attention-status-sync-through-phase476
title: "Phase 477 attention/status sync through Phase 476"
status: approved
implementation_ready: true
date: "2026-07-09"
owner: company-boost
lane: company-boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 477, executor limited to status docs/tests plus non-final parent-verification handoff."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase477, company-boost]
---

# Phase 477 attention/status sync through Phase 476

## Scope

This bounded S1 handoff covers only the Phase 477 status-sync artifacts. The executor must keep work limited to the current-status source of truth, the focused status regression, and this Phase 477 feature `design.md` / `checklist.yaml`.

## Lifecycle

This is S1 only. Parent verification remains required after executor/controller gates. Do not create `acceptance.md`; keep the checklist non-final with `workflow_status`, `acceptance_state`, and parent-verification fields pending. The new status-sync label records synchronization through accepted Phase 476 only; parent closeout owns acceptance.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, build, cache, or service lifecycle changes.
- No root design, README, architecture, roadmap, requirements, compound docs, or later-phase work.
- No out-of-scope labels, guards, directories, or artifacts.
- No `acceptance.md` creation in S1.
- No Phase 478 scope, labels, ranges, stale guards, directories, acceptance artifacts, or claims.
- No staging, commit, push, or parent-finalization claims.

## Allowed Files

Only these files may be edited or created for this handoff:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-09-hermes-tavern-phase477-attention-status-sync-through-phase476/design.md`
- `design/codestable/features/2026-07-09-hermes-tavern-phase477-attention-status-sync-through-phase476/checklist.yaml`

## Prohibited Files

Do not edit any file outside the allowed list. Explicitly prohibited paths include:

- `run_agent.py`
- `cli.py`
- `gateway/run.py`
- any `design/codestable/features/*phase478*` path
- `design/codestable/features/2026-07-09-hermes-tavern-phase477-attention-status-sync-through-phase476/acceptance.md`

## Safety And Compatibility Boundaries

Hermes-native plugin architecture, SillyTavern asset compatibility, adult-fiction/RP compatibility, provider safety boundaries, credential handling, gateway behavior, and service lifecycle behavior are unchanged. Do not introduce minors/CSAM behavior or provider-safety-bypass work.

## Exact Status And Test Contract

### attention.md

- Advance the single current-status line to start with `Current status (2026-06-18): All phases 1-477 accepted`.
- Append exactly one label: `Phase 477 attention status sync through Phase 476`.
- Preserve all prior required labels, including the Phase 121-167 aggregate and all Phase 168-476 labels.
- Preserve placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix must be exactly: `Phase 475 attention status sync through Phase 474, Phase 476 attention status sync through Phase 475, and Phase 477 attention status sync through Phase 476.`
- Do not add any Phase 478 text.

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-477 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-476 accepted"`
- `STALE_PHASE_MARKER = "1-476"`
- `STALE_PHASE_MARKER_EN_DASH = "1–476"`
- `OLDER_STALE_PHASE_MARKER = "1-475"`
- `OLDER_STALE_PHASE_MARKER_EN_DASH = "1–475"`
- Append `Phase 477 attention status sync through Phase 476` to `REQUIRED_PHASE_LABELS` after Phase 476.
- `FINAL_STATUS_SUFFIX = "Phase 475 attention status sync through Phase 474, Phase 476 attention status sync through Phase 475, and Phase 477 attention status sync through Phase 476."`
- `phase_range = range(168, 478)`
- `aggregate_range = "range(168, 478)"`
- Add `stale_aggregate_range_477 = "".join(["range(168, ", "47", "7", ")"])`.
- Add `stale_aggregate_guard_477 = "".join(["range(168, ", "47", str(7), ")"])`.
- Include `stale_aggregate_range_477` in the existing stale-range tuple.
- Add `assert stale_aggregate_guard_477 not in test` while preserving the existing stale direct guards.
- Preserve anchored assignment-count checks, section-placement guard, all-label guard, Phase 121-167 guard, no-discovery-token guards, and existing stale guards.
- Do not introduce any Phase 478 constant, label, range, stale guard, or acceptance token.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-09-hermes-tavern-phase477-attention-status-sync-through-phase476 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u PYTEST_DISABLE_PLUGIN_AUTOLOAD -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- `static allowed-path/status/range/newline/whitespace/no-later-phase/no-acceptance/no-Phase-478 guard over changed plus untracked files`
- `git diff --check`
- `env -u PYTEST_DISABLE_PLUGIN_AUTOLOAD -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider`

## Risks

- Off-by-one drift between the current-status prefix, stale markers, suffix, and `range(168, 478)` can desynchronize the docs and regression.
- Missing the new split stale aggregate guards for `477` weakens the recurring stale-contract protection.
- Any placement drift, extra dirty paths, `acceptance.md` creation, protected-path edits, or Phase 478 token leakage breaks the bounded-slice contract.

## Parent Handoff

After S1, leave the tree dirty only in the allowed files, leave `acceptance.md` absent, keep checklist lifecycle pending parent verification, avoid commit/push activity, and hand back for parent closeout.
