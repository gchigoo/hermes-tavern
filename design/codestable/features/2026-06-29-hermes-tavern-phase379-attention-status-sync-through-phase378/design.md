---
doc_type: feature-design
feature: 2026-06-29-hermes-tavern-phase379-attention-status-sync-through-phase378
title: "Phase 379 attention/status sync through Phase 378"
status: approved
implementation_ready: true
date: "2026-06-29"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready S1 plan: Phase 379 attention/status sync through accepted Phase 378."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase379, company-boost, parent-handoff]
---

# Phase 379 attention/status sync through Phase 378

## Background / Current Status Evidence

Phase 379 is the correct next bounded CodeStable slice.

Evidence read before materialization and confirmed by the read-only Codex architect pass:

- `design/codestable/attention.md` has one current-status line in `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- That status line currently starts with `Current status (2026-06-18): All phases 1-378 accepted`.
- Its terminal suffix is `Phase 376 attention status sync through Phase 375, Phase 377 attention status sync through Phase 376, and Phase 378 attention status sync through Phase 377.`
- Recent feature directories end at `design/codestable/features/2026-06-29-hermes-tavern-phase378-attention-status-sync-through-phase377/`.
- Phase 378 artifacts are complete: `design.md` is `status: approved`, `checklist.yaml` is `status: accepted`, and `acceptance.md` is `status: accepted`.
- `tests/test_hermes_tavern_codestable_status.py` is pinned to Phase 378: `CURRENT_STATUS_PREFIX` is 1-378, stale prefix/markers are 1-377, `FINAL_STATUS_SUFFIX` ends through Phase 378, and live aggregate range is `range(168, 379)`.
- No Phase 379 feature directory existed at architect read time. The only Phase 379 text hits were Phase 378 prohibitions.
- `git status --short --branch` was clean before S1 materialization: `## main...origin/main`.

## Goals

- Materialize the Phase 379 design/checklist pair for a company-boost S1 parent-handoff slice.
- Advance `design/codestable/attention.md` exactly one status tick from 1-378 to 1-379.
- Append `Phase 379 attention status sync through Phase 378` while preserving all prior Phase 168 through Phase 378 labels and `Phase 121-167`.
- Update the focused status regression to guard the Phase 379 live status contract.
- Keep S1 non-final: leave `acceptance.md` absent and reserve final acceptance/status closeout for the parent controller.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No root design, README, architecture, roadmap, requirements, compound, build, cache, or service lifecycle edits.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction boundary change, minors-related work, or CSAM-related work.
- No Phase 380 or later work.
- No `acceptance.md` during S1.

## Allowed Files

Executor S1 may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-29-hermes-tavern-phase379-attention-status-sync-through-phase378/design.md`
- `design/codestable/features/2026-06-29-hermes-tavern-phase379-attention-status-sync-through-phase378/checklist.yaml`

No `acceptance.md` is allowed for this S1 handoff.

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-378 accepted` to `Current status (2026-06-18): All phases 1-379 accepted`.
- Append exactly once: `Phase 379 attention status sync through Phase 378`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 378 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes: `Phase 377 attention status sync through Phase 376, Phase 378 attention status sync through Phase 377, and Phase 379 attention status sync through Phase 378.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-379 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-378 accepted"`
- `STALE_PHASE_MARKER = "1-378"`
- `STALE_PHASE_MARKER_EN_DASH = "1–378"`
- Append `"Phase 379 attention status sync through Phase 378"` to `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 377 attention status sync through Phase 376, Phase 378 attention status sync through Phase 377, and Phase 379 attention status sync through Phase 378."`
- `phase_range = range(168, 380)`
- `aggregate_range = "range(168, 380)"`
- Add split stale aggregate guard: `stale_aggregate_range_379 = "".join(["range(168, ", "37", "9", ")"])`.
- Include `stale_aggregate_range_379` in the stale assertion tuple.
- Do not leave a contiguous stale literal `range(168, 379)` in the test source after the update. It must be represented only through split pieces.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive literal counts.
- Do not require the newest label exactly once in the test source; it can appear in both `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Stale-Range Guards

The old live aggregate range `range(168, 379)` becomes stale in Phase 379. The focused test must construct that stale value with split pieces and assert the contiguous old literal is absent from the test source.

The negative stale terminal assertion should reject `All phases 1-378 accepted`, including both `1-378` and `1–378`, while allowing historical internal ranges and the explicit `Phase 121-167` label.

The only contiguous live aggregate range literal after S1 should be `range(168, 380)`.

## Structure / Micro-Refactor Boundary

No micro-refactor is scoped. This is a docs/static-test/status-only single-tick update against one long status line and one focused regression test. Creating or editing broader helpers would increase risk and violate the bounded slice.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-29-hermes-tavern-phase379-attention-status-sync-through-phase378/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-29-hermes-tavern-phase379-attention-status-sync-through-phase378/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static Phase 379 status/scope guard, including allowed paths only, no `acceptance.md`, single anchored current/final assignments, all Phase 168-379 labels present, and no contiguous stale `range(168, 379)` literal.
- `git diff --check`
- Optional broader pytest if feasible without installs/services.

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior phase label.
- The terminal `and` can remain on Phase 378 instead of moving to Phase 379.
- `range(168, 379)` is currently live and becomes stale; leaving it contiguous in the test source weakens the stale guard.
- Naive source literal counting can false-fail or miss assignment drift; keep anchored assignment-count guards.
- Accidentally creating `acceptance.md` would cross the S1/S2 boundary.
- Any runtime or safety-policy edit would violate the docs/static-test/status-only scope.

## S1 Handoff

This design scopes S1 only. Executor should update the allowed docs/test files, run focused verification where feasible, leave `acceptance.md` absent, keep checklist/root acceptance statuses non-final, and hand back to the parent/controller for any final verification, acceptance creation, commit, and push.
