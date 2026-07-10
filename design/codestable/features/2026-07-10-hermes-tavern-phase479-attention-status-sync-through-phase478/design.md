---
doc_type: feature-design
feature: 2026-07-10-hermes-tavern-phase479-attention-status-sync-through-phase478
title: "Phase 479 attention/status sync through Phase 478"
status: approved
implementation_ready: true
date: "2026-07-10"
owner: standard-lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Approved standard-lane S1 design for Phase 479; executor gpt-5.4 is limited to status docs/tests plus non-final parent-controller handoff."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase479, standard]
---

# Phase 479 attention/status sync through Phase 478

## Scope

This bounded S1 handoff covers only the Phase 479 status-sync artifacts. The executor is limited to the current-status source of truth, the focused status regression, and this feature's `design.md` and `checklist.yaml`.

## Lifecycle

Architect artifact precedes executor implementation. S1 remains non-final: the executor must not create `acceptance.md`, commit, push, or claim parent verification. The parent controller owns verification, acceptance, commit, and push.

## Allowed Files

S1 may edit only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-10-hermes-tavern-phase479-attention-status-sync-through-phase478/design.md`
- `design/codestable/features/2026-07-10-hermes-tavern-phase479-attention-status-sync-through-phase478/checklist.yaml`

Parent closeout may additionally create `design/codestable/features/2026-07-10-hermes-tavern-phase479-attention-status-sync-through-phase478/acceptance.md`.

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, build, cache, or service-lifecycle changes.
- No root design, README, architecture, roadmap, requirements, compound docs, reviews, refactors, or later-phase work.
- No Phase 480 label, artifact, acceptance claim, or implementation work. `range(168, 480)` is only the Phase 479 end-exclusive aggregate range.
- No minors/CSAM behavior and no provider-safety bypass work.

## Exact Contract

### attention.md

- Advance the single current-status line to `Current status (2026-06-18): All phases 1-479 accepted`.
- Append exactly one `Phase 479 attention status sync through Phase 478` label.
- Preserve the Phase 121-167 aggregate and every Phase 168-478 label.
- Preserve placement under `### 其他`, immediately after the adult-fiction boundary and before `### Hermes Tavern 凭证约束`.
- End exactly with `Phase 477 attention status sync through Phase 476, Phase 478 attention status sync through Phase 477, and Phase 479 attention status sync through Phase 478.`

### Focused status test

- Advance current/stale prefixes and markers from terminal Phase 478 to 479.
- Keep Phase 477 as the older stale marker.
- Append the Phase 479 required label after Phase 478.
- Advance `phase_range` and `aggregate_range` from `range(168, 479)` to `range(168, 480)`.
- Add and assert split stale guards for `range(168, 479)` using `stale_aggregate_range_479` and `stale_aggregate_guard_479`.
- Preserve anchored assignment-count checks, section placement, all labels, the Phase 121-167 guard, all prior stale guards, and no-discovery-token guards.

## Acceptance Criteria

- S1 touches only the four allowed files and leaves `acceptance.md` absent.
- The attention status line and focused regression satisfy the exact contract.
- No Phase 480 work or protected-scope edits exist.
- Hermes-native plugin architecture, SillyTavern compatibility, adult-fiction/RP compatibility, credentials, gateway behavior, and provider-safety boundaries remain unchanged.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-10-hermes-tavern-phase479-attention-status-sync-through-phase478 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u PYTEST_DISABLE_PLUGIN_AUTOLOAD -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- `git diff --check`
- `TMPDIR=/tmp env -u PYTEST_DISABLE_PLUGIN_AUTOLOAD -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider`
