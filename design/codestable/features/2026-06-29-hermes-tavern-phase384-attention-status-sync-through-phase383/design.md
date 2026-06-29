---
doc_type: feature-design
feature: 2026-06-29-hermes-tavern-phase384-attention-status-sync-through-phase383
title: "Phase 384 attention/status sync through Phase 383"
status: approved
implementation_ready: true
date: "2026-06-29"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready S1 parent-handoff plan: Phase 384 attention/status sync through accepted Phase 383."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase384, company-boost, parent-handoff]
---

# Phase 384 attention/status sync through Phase 383

## Background / Current Status Evidence

Phase 384 is the correct next bounded CodeStable slice.

Evidence confirmed by the read-only Codex architect pass:

- Repository branch is `main` at `a46631a`; controller preflight and post-architect status showed no changed repo files before materializing this slice.
- CodeStable root is `design/codestable`.
- `design/codestable/attention.md` is the startup attention source of truth.
- `design/codestable/attention.md` has one current-status line in `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- That status line currently starts with `Current status (2026-06-18): All phases 1-383 accepted`.
- Its terminal suffix is `Phase 381 attention status sync through Phase 380, Phase 382 attention status sync through Phase 381, and Phase 383 attention status sync through Phase 382.`
- Phase 383 artifacts are complete and accepted: `design.md` is `status: approved`, `checklist.yaml` is `status: accepted`, and `acceptance.md` is `status: accepted`.
- `tests/test_hermes_tavern_codestable_status.py` is pinned to Phase 383: `CURRENT_STATUS_PREFIX` is 1-383, stale prefix/markers are 1-382, `FINAL_STATUS_SUFFIX` ends through Phase 383, and live aggregate range is `range(168, 384)`.
- The focused test preserves anchored assignment-count guards, the current-status section-placement guard, and self-source guards against `.glob`, `.rglob`, `iterdir`, and `os.walk` discovery tokens.
- No Phase 384 feature directory existed at architect read time.

## Goals

- Materialize the Phase 384 design/checklist pair for a company-boost S1 parent-handoff slice.
- Advance `design/codestable/attention.md` exactly one status tick from 1-383 to 1-384.
- Append `Phase 384 attention status sync through Phase 383` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 383 label.
- Update the focused status regression to guard the Phase 384 live status contract.
- Keep S1 non-final: leave `acceptance.md` absent and reserve final acceptance/status closeout for the parent controller.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No build, root-design, README, architecture, roadmap, requirements, or compound changes.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction boundary change, RP compatibility change, minors-related work, or CSAM-related work.
- No Phase 385 or later work.
- No `acceptance.md` during S1.

## Allowed Files

Executor S1 may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-29-hermes-tavern-phase384-attention-status-sync-through-phase383/design.md`
- `design/codestable/features/2026-06-29-hermes-tavern-phase384-attention-status-sync-through-phase383/checklist.yaml`

No `acceptance.md` is allowed for this S1 handoff.

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-383 accepted` to `Current status (2026-06-18): All phases 1-384 accepted`.
- Append exactly once in the attention status line: `Phase 384 attention status sync through Phase 383`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 383 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes: `Phase 382 attention status sync through Phase 381, Phase 383 attention status sync through Phase 382, and Phase 384 attention status sync through Phase 383.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-384 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-383 accepted"`
- `STALE_PHASE_MARKER = "1-383"`
- `STALE_PHASE_MARKER_EN_DASH = "1–383"`
- Append `"Phase 384 attention status sync through Phase 383"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 383 required label.
- `FINAL_STATUS_SUFFIX = "Phase 382 attention status sync through Phase 381, Phase 383 attention status sync through Phase 382, and Phase 384 attention status sync through Phase 383."`
- `phase_range = range(168, 385)`
- `aggregate_range = "range(168, 385)"`
- Add a split stale aggregate guard for the immediately previous terminal range: `stale_aggregate_range_384 = "".join(["range(168, ", "38", "4", ")"])`.
- Include `stale_aggregate_range_384` in the stale assertion tuple.
- Preserve the existing split stale guard for `range(168, 383)` in the stale assertion tuple.
- Replace the final split `stale_aggregate_guard` so it also builds `range(168, 384)` without embedding that stale literal contiguously anywhere in the test source.
- Do not leave a contiguous stale literal `range(168, 384)` in the test source after the update.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive substring counts.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Preserve self-source guards against `.glob`, `.rglob`, `iterdir`, and `os.walk` discovery tokens.
- Add or preserve an exact-once check for the newest label on the attention status line only. The newest label may appear in both `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`, so no exact-once assertion should be applied to the whole test source.

## Structure / Micro-Refactor Boundary

No micro-refactor is scoped. This is a docs/static-test/status-only single-tick update against one long status line and one focused regression test. Creating helpers, changing runtime paths, or touching wider docs would increase risk and violate the bounded slice.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-29-hermes-tavern-phase384-attention-status-sync-through-phase383/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-29-hermes-tavern-phase384-attention-status-sync-through-phase383/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static Phase 384 status/scope guard using changed plus untracked files.
- Parent-owned broader pytest gate if requested by the controller.
- `git diff --check`

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior phase label.
- The terminal `and` can remain on Phase 383 instead of moving to Phase 384.
- `range(168, 384)` is currently live and becomes stale; leaving it contiguous in the test source weakens the stale guard.
- Naive source literal counting can false-fail because the newest label legitimately appears in both `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.
- Accidentally creating `acceptance.md` would cross the S1/S2 boundary.
- Any runtime, provider, gateway, CLI, config, dependency, build, root-design, README, architecture, roadmap, requirements, compound, safety, minors/CSAM, or provider-bypass change would violate the docs/static-test/status-only scope.

## S1 Handoff

This design scopes S1 only. Executor should update the allowed docs/test files, run focused verification where feasible, leave `acceptance.md` absent, keep checklist/root acceptance statuses non-final with `parent_verification_required: true`, and hand back to the parent/controller for final verification, acceptance creation, commit, and push.
