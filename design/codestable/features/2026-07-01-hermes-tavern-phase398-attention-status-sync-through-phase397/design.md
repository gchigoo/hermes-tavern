---
doc_type: feature-design
feature: 2026-07-01-hermes-tavern-phase398-attention-status-sync-through-phase397
title: "Phase 398 attention/status sync through Phase 397"
status: approved
implementation_ready: true
date: "2026-07-01"
owner: company_boost_lane
lane: company-boost/uncommitted
bounded_phase: "docs/static-test/status-only"
summary: "Approved design for Phase 398 attention/status sync through accepted Phase 397; parent verification and acceptance closeout passed."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase398, company-boost]
---

# Phase 398 attention/status sync through Phase 397

## Background / Current Status Evidence

Phase 398 is the correct next bounded CodeStable slice for this company-boost lane.

Read-only architect evidence:

- Git is on `main` at `0cfe279` with a clean working tree before this slice.
- `design/codestable/attention.md` has exactly one current-status line, currently synced through `All phases 1-397 accepted`.
- Phase 397 artifacts are complete and accepted under `design/codestable/features/2026-07-01-hermes-tavern-phase397-attention-status-sync-through-phase396/`.
- `tests/test_hermes_tavern_codestable_status.py` is pinned to Phase 397: current/stale constants are 397/396, live range is `range(168, 398)`, aggregate string is `"range(168, 398)"`, and the split stale guard reaches `stale_aggregate_range_397`.
- `Phase 121-167` and explicit Phase 168 through Phase 397 labels are present.
- No Phase 398 feature directory existed at architect read time.

## Goals

- Materialize the Phase 398 design/checklist pair for a company-boost S1 handoff slice.
- Advance `design/codestable/attention.md` exactly one status tick from 1-397 to 1-398.
- Append `Phase 398 attention status sync through Phase 397` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 397 label.
- Update the focused status regression to guard the Phase 398 live status contract.
- Keep S1 non-final: leave `acceptance.md` absent and reserve final acceptance/status closeout for the parent controller.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No root-design, README, architecture, roadmap, requirements, compound, build, or cache changes.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes by executor.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction policy change, RP compatibility change, minors-related work, or CSAM-related work.
- No Phase 399 or later work.
- No S2 closeout by executor.
- No `acceptance.md` during S1.

## Allowed Files

Executor S1 may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-01-hermes-tavern-phase398-attention-status-sync-through-phase397/design.md`
- `design/codestable/features/2026-07-01-hermes-tavern-phase398-attention-status-sync-through-phase397/checklist.yaml`

No `acceptance.md` is allowed for this S1 handoff.

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-397 accepted` to `Current status (2026-06-18): All phases 1-398 accepted`.
- Append exactly once in the attention status line: `Phase 398 attention status sync through Phase 397`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 397 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes exactly: `Phase 396 attention status sync through Phase 395, Phase 397 attention status sync through Phase 396, and Phase 398 attention status sync through Phase 397.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-398 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-397 accepted"`
- `STALE_PHASE_MARKER = "1-397"`
- `STALE_PHASE_MARKER_EN_DASH = "1–397"`
- Append `"Phase 398 attention status sync through Phase 397"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 397 required label.
- `FINAL_STATUS_SUFFIX = "Phase 396 attention status sync through Phase 395, Phase 397 attention status sync through Phase 396, and Phase 398 attention status sync through Phase 397."`
- `phase_range = range(168, 399)`
- `aggregate_range = "range(168, 399)"`
- Add `stale_aggregate_range_398 = "".join(["range(168, ", "39", "8", ")"])`.
- Include `stale_aggregate_range_398` in the stale assertion tuple.
- Preserve prior split stale guards, including `stale_aggregate_range_397` and earlier.
- Replace the final split `stale_aggregate_guard` so it builds stale `range(168, 398)` without embedding contiguous `range(168, 398)` in the test source.
- Do not leave a contiguous stale literal `range(168, 398)` in the test source after the update; the live range is `range(168, 399)`.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive substring counts.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Preserve split no-discovery-token guards against `.glob`, `.rglob`, `iterdir`, and `os.walk`.
- Newest-label exact-once applies to the attention status line only. Do not require exact once across the test source because the newest label appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Static Guard Requirements

Controller verification must reject the implementation unless all changed/untracked paths are exactly the four allowed S1 paths listed above, `acceptance.md` is absent, and no runtime/source/plugin/provider/gateway/CLI/config/dependency/root-design/README/architecture/roadmap/requirements/compound/build/cache path changed.

Static checks must verify the exact current-status prefix, stale prefix, stale hyphen/en-dash markers, final suffix, preservation of `Phase 121-167`, preservation of every explicit Phase 168 through Phase 397 label, append of Phase 398 exactly once in the attention status line, current-status section placement, anchored assignment-count guards, no direct stale `range(168, 398)` literal in the focused test source except the live aggregate range is `range(168, 399)`, no discovery tokens, final newlines, and no trailing whitespace.

## Structure Health / Microrefactor Decision

No microrefactor is part of this slice. The only planned work is a bounded status-line update, a focused static regression update, and creation of the selected Phase 398 feature artifacts. Changing runtime structure, plugin/provider boundaries, root design, architecture, roadmap, requirements, or compound documents would be outside scope.

## Verification Commands

Worker/controller verification after S1 should run:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase398-attention-status-sync-through-phase397/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase398-attention-status-sync-through-phase397/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static Phase 398 status/scope/final-newline/trailing-whitespace guard using changed plus untracked files.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='`
- `git diff --check`

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior explicit phase label.
- The terminal `and` must move to Phase 398; Phase 397 should become comma-separated.
- `range(168, 398)` becomes stale and must not remain as a contiguous stale literal in the focused test source.
- Existing split stale guards, especially `stale_aggregate_range_397`, must remain present in the stale tuple.
- Newest-label exact-once applies only to the attention status line, not to the whole test source.
- Accidentally creating `acceptance.md` in S1 would cross the S1/S2 boundary.
- Any runtime, provider, gateway, CLI, config, dependency, build, root-design, README, architecture, roadmap, requirements, compound, safety, minors/CSAM, or provider-bypass change would violate scope.

## Rollback

If rollback is required before parent closeout, restore only `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` from HEAD and remove only `design/codestable/features/2026-07-01-hermes-tavern-phase398-attention-status-sync-through-phase397/`. Do not stage, commit, or push during rollback.

## S1 Handoff

This design scopes S1 only. Executor should update the allowed docs/test files, leave `acceptance.md` absent, keep checklist/root acceptance statuses non-final with `parent_verification_required: true`, avoid staging/commit/push, avoid marking parent/controller checks final, and hand back to the parent/controller for final verification and any later acceptance/commit/push closeout.
