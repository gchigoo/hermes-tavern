---
doc_type: feature-design
feature: 2026-06-29-hermes-tavern-phase382-attention-status-sync-through-phase381
title: "Phase 382 attention/status sync through Phase 381"
status: approved
implementation_ready: true
date: "2026-06-29"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready S1 parent-handoff plan: Phase 382 attention/status sync through accepted Phase 381."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase382, company-boost, parent-handoff]
---

# Phase 382 attention/status sync through Phase 381

## Background / Current Status Evidence

Phase 382 is the correct next bounded CodeStable slice.

Evidence confirmed by the read-only Codex architect pass:

- `design/codestable/attention.md` has one current-status line in `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- That status line currently starts with `Current status (2026-06-18): All phases 1-381 accepted`.
- Its terminal suffix is `Phase 379 attention status sync through Phase 378, Phase 380 attention status sync through Phase 379, and Phase 381 attention status sync through Phase 380.`
- Phase 381 artifacts are complete and accepted: `design.md` is `status: approved`, `checklist.yaml` is `status: accepted`, and `acceptance.md` is `status: accepted`.
- `tests/test_hermes_tavern_codestable_status.py` is pinned to Phase 381: `CURRENT_STATUS_PREFIX` is 1-381, stale prefix/markers are 1-380, `FINAL_STATUS_SUFFIX` ends through Phase 381, and live aggregate range is `range(168, 382)`.
- No Phase 382 feature directory existed at architect read time.
- `git rev-parse --short HEAD` returned `b160c56`; `git status --porcelain=v1 --untracked-files=all` showed no file entries before materialization.

## Goals

- Materialize the Phase 382 design/checklist pair for a company-boost S1 parent-handoff slice.
- Advance `design/codestable/attention.md` exactly one status tick from 1-381 to 1-382.
- Append `Phase 382 attention status sync through Phase 381` while preserving all prior Phase 168 through Phase 381 labels and `Phase 121-167`.
- Update the focused status regression to guard the Phase 382 live status contract.
- Keep S1 non-final: leave `acceptance.md` absent and reserve final acceptance/status closeout for the parent controller.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No root design, README, architecture, roadmap, requirements, compound, build, cache, or service lifecycle edits.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction boundary change, minors-related work, or CSAM-related work.
- No Phase 383 or later work.
- No `acceptance.md` during this worker/S1 handoff.

## Allowed Files

Executor S1 may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-29-hermes-tavern-phase382-attention-status-sync-through-phase381/design.md`
- `design/codestable/features/2026-06-29-hermes-tavern-phase382-attention-status-sync-through-phase381/checklist.yaml`

No `acceptance.md` is allowed for this S1 handoff.

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-381 accepted` to `Current status (2026-06-18): All phases 1-382 accepted`.
- Append exactly once: `Phase 382 attention status sync through Phase 381`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 381 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes: `Phase 380 attention status sync through Phase 379, Phase 381 attention status sync through Phase 380, and Phase 382 attention status sync through Phase 381.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-382 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-381 accepted"`
- `STALE_PHASE_MARKER = "1-381"`
- `STALE_PHASE_MARKER_EN_DASH = "1–381"`
- Append `"Phase 382 attention status sync through Phase 381"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 381 required label.
- `FINAL_STATUS_SUFFIX = "Phase 380 attention status sync through Phase 379, Phase 381 attention status sync through Phase 380, and Phase 382 attention status sync through Phase 381."`
- `phase_range = range(168, 383)`
- `aggregate_range = "range(168, 383)"`
- Add split stale aggregate guard: `stale_aggregate_range_382 = "".join(["range(168, ", "38", "2", ")"])`.
- Include `stale_aggregate_range_382` in the stale assertion tuple.
- Replace the final split `stale_aggregate_guard` so it builds `range(168, 382)`.
- Do not leave a contiguous stale literal `range(168, 382)` in the test source after the update.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Do not require the newest label exactly once in the test source; it can appear in both `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Structure / Micro-Refactor Boundary

No micro-refactor is scoped. This is a docs/static-test/status-only single-tick update against one long status line and one focused regression test. Creating helpers, changing runtime paths, or touching wider docs would increase risk and violate the bounded slice.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-29-hermes-tavern-phase382-attention-status-sync-through-phase381/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-29-hermes-tavern-phase382-attention-status-sync-through-phase381/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static Phase 382 status/scope guard using changed plus untracked files.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider`
- `git diff --check`

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior phase label.
- The terminal `and` can remain on Phase 381 instead of moving to Phase 382.
- `range(168, 382)` is currently live and becomes stale; leaving it contiguous in the test source weakens the stale guard.
- Naive source literal counting can false-fail or miss assignment drift; keep anchored assignment-count guards.
- Accidentally creating `acceptance.md` would cross the S1/S2 boundary.
- Any runtime or safety-policy edit would violate the docs/static-test/status-only scope.

## S1 Handoff

This design scopes S1 only. Executor should update the allowed docs/test files, run focused verification where feasible, leave `acceptance.md` absent, keep checklist/root acceptance statuses non-final, and hand back to the parent/controller for final verification, acceptance creation, commit, and push.
