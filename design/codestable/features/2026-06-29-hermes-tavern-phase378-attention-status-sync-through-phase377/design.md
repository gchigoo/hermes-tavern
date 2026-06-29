---
doc_type: feature-design
feature: 2026-06-29-hermes-tavern-phase378-attention-status-sync-through-phase377
title: "Phase 378 attention/status sync through Phase 377"
status: approved
implementation_ready: true
date: "2026-06-29"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 378 attention/status sync through accepted Phase 377."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase378, company-boost, parent-handoff]
---

# Phase 378 attention/status sync through Phase 377

## Background / Current Status Evidence

Phase 378 is the correct next bounded slice.

Evidence read at architect time:

- `design/codestable/attention.md` has one current-status line under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- That status line currently starts with `Current status (2026-06-18): All phases 1-377 accepted`.
- Its terminal suffix is `Phase 375 attention status sync through Phase 374, Phase 376 attention status sync through Phase 375, and Phase 377 attention status sync through Phase 376.`
- Recent feature directories end at `design/codestable/features/2026-06-29-hermes-tavern-phase377-attention-status-sync-through-phase376`.
- `design/codestable/features/2026-06-29-hermes-tavern-phase377-attention-status-sync-through-phase376/acceptance.md` exists and has `status: accepted`.
- No `phase378` feature directory exists at architect read time.
- `tests/test_hermes_tavern_codestable_status.py` is pinned to Phase 377: `CURRENT_STATUS_PREFIX` is 1-377, stale prefix/markers are 1-376, `phase_range = range(168, 378)`, and `aggregate_range = "range(168, 378)"`.
- The focused test already uses anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.

## Goals

- Materialize this Phase 378 design/checklist pair for S1 company-boost handoff.
- Advance `design/codestable/attention.md` exactly one status tick from 1-377 to 1-378.
- Append `Phase 378 attention status sync through Phase 377` exactly once.
- Preserve every prior phase label, especially Phase 375, Phase 376, and Phase 377.
- Update the focused status regression to guard the Phase 378 live status contract.
- Keep S1 non-final: leave `acceptance.md` absent.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No root design, architecture, roadmap, requirements, compound, build, cache, or service lifecycle edits.
- No broad rewrites.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction boundary change, minors-related work, or CSAM-related work.
- No staging, commit, push, dependency install, network call, or service start.
- No Phase 379 or later work.
- No `acceptance.md` during S1.

## Allowed Files

Executor S1 may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-29-hermes-tavern-phase378-attention-status-sync-through-phase377/design.md`
- `design/codestable/features/2026-06-29-hermes-tavern-phase378-attention-status-sync-through-phase377/checklist.yaml`

No `acceptance.md` is allowed for S1.

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-377 accepted` to `Current status (2026-06-18): All phases 1-378 accepted`.
- Append exactly once: `Phase 378 attention status sync through Phase 377`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 377 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes: `Phase 376 attention status sync through Phase 375, Phase 377 attention status sync through Phase 376, and Phase 378 attention status sync through Phase 377.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-378 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-377 accepted"`
- `STALE_PHASE_MARKER = "1-377"`
- `STALE_PHASE_MARKER_EN_DASH = "1–377"`
- Append `"Phase 378 attention status sync through Phase 377"` to `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 376 attention status sync through Phase 375, Phase 377 attention status sync through Phase 376, and Phase 378 attention status sync through Phase 377."`
- `phase_range = range(168, 379)`
- `aggregate_range = "range(168, 379)"`
- Add split stale aggregate guard: `stale_aggregate_range_378 = "".join(["range(168, ", "37", "8", ")"])`
- Include `stale_aggregate_range_378` in the stale assertion tuple.
- Do not leave a contiguous stale literal `range(168, 378)` in the test source after the update. It must be represented only through split pieces.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive literal counts.

## Stale-Range Guards

The old live aggregate range `range(168, 378)` becomes stale in Phase 378. The focused test must construct that stale value with split pieces and assert the contiguous old literal is absent from the test source.

The only contiguous live aggregate range literal after S1 should be `range(168, 379)`.

## Structure / Micro-Refactor Boundary

No micro-refactor is scoped. This is a docs/static-test/status-only single-tick update against one long status line and one focused regression test. Creating or editing broader helpers would increase risk and violate the bounded slice.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-29-hermes-tavern-phase378-attention-status-sync-through-phase377/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-29-hermes-tavern-phase378-attention-status-sync-through-phase377/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static source/status guard from `checklist.yaml`, including no contiguous stale `range(168, 378)` literal.
- `test ! -e design/codestable/features/2026-06-29-hermes-tavern-phase378-attention-status-sync-through-phase377/acceptance.md`
- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider` if feasible without installing dependencies or starting services.

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior phase label.
- The terminal `and` can remain on Phase 377 instead of moving to Phase 378.
- `range(168, 378)` is currently live and becomes stale; leaving it contiguous in the test source weakens the stale guard.
- Naive source literal counting can false-fail or miss assignment drift; keep anchored assignment-count guards.
- Accidentally creating `acceptance.md` would cross the S1/S2 boundary.
- Any runtime or safety-policy edit would violate the docs/static-test/status-only scope.

## S1 Handoff

This design scopes S1 only. Executor should update the allowed docs/test files, run focused verification, leave `acceptance.md` absent, and hand back to the parent/controller for any S2 acceptance closeout.
