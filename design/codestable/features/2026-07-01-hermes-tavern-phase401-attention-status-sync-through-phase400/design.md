---
doc_type: feature-design
feature: 2026-07-01-hermes-tavern-phase401-attention-status-sync-through-phase400
title: "Phase 401 attention/status sync through Phase 400"
status: approved
implementation_ready: true
date: "2026-07-01"
owner: company_boost_lane
lane: company-boost/uncommitted
bounded_phase: "docs/static-test/status-only"
summary: "Approved design for Phase 401 attention/status sync through accepted Phase 400; worker/controller verification and no-commit handoff are required."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase401, company-boost]
---

# Phase 401 attention/status sync through Phase 400

## Background / Current Status Evidence

Phase 401 is the correct next bounded CodeStable slice for this company-boost lane.

Read-only architect evidence:

- Git was on `main` with a clean working tree before this slice.
- `design/codestable/attention.md` had exactly one current-status line, synced through `All phases 1-400 accepted`.
- Phase 400 artifacts were complete and accepted under `design/codestable/features/2026-07-01-hermes-tavern-phase400-attention-status-sync-through-phase399/`.
- `tests/test_hermes_tavern_codestable_status.py` was pinned to Phase 400: current/stale constants were 400/399, live range was `range(168, 401)`, aggregate string was `"range(168, 401)"`, and the split stale guard reached `stale_aggregate_range_400`.
- `Phase 121-167` and explicit Phase 168 through Phase 400 labels were present.
- No Phase 401 feature directory existed at architect read time.

## Goals

- Materialize the Phase 401 design/checklist/acceptance artifact set for a company-boost dirty-tree handoff.
- Advance `design/codestable/attention.md` exactly one status tick from 1-400 to 1-401.
- Append `Phase 401 attention status sync through Phase 400` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 400 label.
- Update the focused status regression to guard the Phase 401 live status contract.
- Record truthful worker/controller verification evidence without staging, committing, or pushing.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No root-design, README, architecture, roadmap, requirements, compound, build, or cache changes.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction policy change, RP compatibility change, minors-related work, or CSAM-related work.
- No Phase 402 or later work.

## Allowed Files

Only these files are in scope:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-01-hermes-tavern-phase401-attention-status-sync-through-phase400/design.md`
- `design/codestable/features/2026-07-01-hermes-tavern-phase401-attention-status-sync-through-phase400/checklist.yaml`
- `design/codestable/features/2026-07-01-hermes-tavern-phase401-attention-status-sync-through-phase400/acceptance.md`

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-400 accepted` to `Current status (2026-06-18): All phases 1-401 accepted`.
- Append exactly once in the attention status line: `Phase 401 attention status sync through Phase 400`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 400 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes exactly: `Phase 399 attention status sync through Phase 398, Phase 400 attention status sync through Phase 399, and Phase 401 attention status sync through Phase 400.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-401 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-400 accepted"`
- `STALE_PHASE_MARKER = "1-400"`
- `STALE_PHASE_MARKER_EN_DASH = "1–400"`
- Append `"Phase 401 attention status sync through Phase 400"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 400 required label.
- `FINAL_STATUS_SUFFIX = "Phase 399 attention status sync through Phase 398, Phase 400 attention status sync through Phase 399, and Phase 401 attention status sync through Phase 400."`
- `phase_range = range(168, 402)`
- `aggregate_range = "range(168, 402)"`
- Add `stale_aggregate_range_401 = "".join(["range(168, ", "40", "1", ")"])`.
- Include `stale_aggregate_range_401` in the stale assertion tuple.
- Preserve prior split stale guards, including `stale_aggregate_range_400` and earlier.
- Replace the final split `stale_aggregate_guard` so it builds stale `range(168, 401)` without embedding contiguous `range(168, 401)` in the test source.
- Do not leave a contiguous stale literal `range(168, 401)` in the test source after the update; the live range is `range(168, 402)`.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive substring counts.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Preserve split no-discovery-token guards against `.glob`, `.rglob`, `iterdir`, and `os.walk`.
- Newest-label exact-once applies to the attention status line only. Do not require exact once across the test source because the newest label appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Static Guard Requirements

Controller verification must reject the implementation unless all changed/untracked paths are exactly the five allowed Phase 401 paths listed above and no runtime/source/plugin/provider/gateway/CLI/config/dependency/root-design/README/architecture/roadmap/requirements/compound/build/cache path changed.

Static checks must verify the exact current-status prefix, stale prefix, stale hyphen/en-dash markers, final suffix, preservation of `Phase 121-167`, preservation of every explicit Phase 168 through Phase 400 label, append of Phase 401 exactly once in the attention status line, current-status section placement, anchored assignment-count guards, no direct stale `range(168, 401)` literal in the focused test source, no discovery tokens, final newlines, and no trailing whitespace.

## Structure Health / Microrefactor Decision

No microrefactor is part of this slice. The only planned work is a bounded status-line update, a focused static regression update, and creation/finalization of the selected Phase 401 feature artifacts. Changing runtime structure, plugin/provider boundaries, root design, architecture, roadmap, requirements, or compound documents would be outside scope.

## Verification Commands

Worker/controller verification after implementation must run:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase401-attention-status-sync-through-phase400/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase401-attention-status-sync-through-phase400/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase401-attention-status-sync-through-phase400/acceptance.md --require doc_type --require feature --require status --require accepted_at --require owner --require lane --require bounded_phase --require tags`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase401 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static Phase 401 status/scope/final-newline/trailing-whitespace guard using changed plus untracked files.
- `git diff --check`

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior explicit phase label.
- The terminal `and` must move to Phase 401; Phase 400 should become comma-separated.
- `range(168, 401)` becomes stale and must not remain as a contiguous stale literal in the focused test source.
- Existing split stale guards, especially `stale_aggregate_range_400`, must remain present in the stale tuple.
- Newest-label exact-once applies only to the attention status line, not to the whole test source.
- Any runtime, provider, gateway, CLI, config, dependency, build, root-design, README, architecture, roadmap, requirements, compound, safety, minors/CSAM, or provider-bypass change would violate scope.

## Rollback

If rollback is required before parent closeout, restore only `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` from HEAD and remove only `design/codestable/features/2026-07-01-hermes-tavern-phase401-attention-status-sync-through-phase400/`. Do not stage, commit, or push during rollback.

## Handoff

This design scopes one complete Phase 401 status-sync dirty-tree handoff. Executor should update only the allowed docs/test files, avoid staging/commit/push, avoid prohibited paths, and hand back to the worker/controller for real verification and truthful acceptance/checklist finalization before the parent controller reruns gates and decides whether to commit/push.
