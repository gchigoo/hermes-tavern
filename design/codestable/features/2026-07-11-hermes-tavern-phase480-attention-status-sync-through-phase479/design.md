---
doc_type: feature-design
feature: 2026-07-11-hermes-tavern-phase480-attention-status-sync-through-phase479
title: "Phase 480 attention/status sync through Phase 479"
status: approved
implementation_ready: true
date: "2026-07-11"
owner: standard-lane
lane: standard
architect_model: gpt-5.5
architect_reasoning: xhigh
bounded_phase: "docs/static-test/status-only"
summary: "Approved standard-lane S1 design for Phase 480; executor is limited to status docs/tests plus non-final parent-controller handoff."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase480, standard]
---

# Phase 480 attention/status sync through Phase 479

## Scope

This bounded S1 handoff covers only the Phase 480 status-sync artifacts. The executor is limited to the current-status source of truth, the focused status regression, and this feature's `design.md` and `checklist.yaml`.

## Lifecycle

Architect artifact precedes executor implementation. S1 remains non-final: the executor must not create `acceptance.md`, commit, push, or claim parent verification. The parent controller owns verification, acceptance, commit, and push. `acceptance.md` must remain absent during executor S1 and may be created only after parent verification.

## Allowed Files

S1 may edit only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-11-hermes-tavern-phase480-attention-status-sync-through-phase479/design.md`
- `design/codestable/features/2026-07-11-hermes-tavern-phase480-attention-status-sync-through-phase479/checklist.yaml`

Parent closeout may additionally create `design/codestable/features/2026-07-11-hermes-tavern-phase480-attention-status-sync-through-phase479/acceptance.md` only after verification.

## Prohibited Scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, build, cache, or service-lifecycle changes.
- No root design, README, architecture, roadmap, requirements, compound docs, reviews, refactors, or broader implementation work.
- No Phase 481 label, artifact, acceptance claim, or implementation work. `range(168, 481)` is only the Phase 480 end-exclusive aggregate range.
- No minors/CSAM behavior and no provider-safety bypass work.

## Exact Contract

### attention.md

- Advance the single current-status line to `Current status (2026-06-18): All phases 1-480 accepted`.
- Preserve the Phase 121-167 aggregate and every existing Phase 168-479 label.
- Append exactly one `Phase 480 attention status sync through Phase 479` label.
- Preserve placement under `### 其他`, immediately after the adult-fiction boundary and before `### Hermes Tavern 凭证约束`.
- End exactly with `Phase 478 attention status sync through Phase 477, Phase 479 attention status sync through Phase 478, and Phase 480 attention status sync through Phase 479.`

### Focused status test

- Advance current/stale/older terminal markers coherently:
  - current: `1-480`
  - stale: `1-479` and `1–479`
  - older stale: `1-478` and `1–478`
- Append the Phase 480 required label after Phase 479.
- Advance `phase_range` and `aggregate_range` from `range(168, 480)` to `range(168, 481)`.
- Add and assert split stale guards for superseded `range(168, 480)`:
  - `stale_aggregate_range_480 = "".join(["range(168, ", "48", "0", ")"])`
  - `stale_aggregate_guard_480 = "".join(["range(168, ", "48", str(0), ")"])`
- Preserve all prior split stale guards, anchored assignment-count checks, section placement checks, all-label checks, the Phase 121-167 aggregate guard, and no-discovery-token guards.

## Acceptance Criteria

- S1 touches only the four allowed files and leaves `acceptance.md` absent.
- The attention status line and focused regression satisfy the exact contract.
- No Phase 481 work or protected-scope edits exist.
- Hermes-native plugin architecture, SillyTavern compatibility, adult-fiction/RP compatibility, credentials, gateway behavior, and provider-safety boundaries remain unchanged.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-11-hermes-tavern-phase480-attention-status-sync-through-phase479 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u PYTEST_DISABLE_PLUGIN_AUTOLOAD -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- `git diff --check`
- `TMPDIR=/tmp env -u PYTEST_DISABLE_PLUGIN_AUTOLOAD -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider`
