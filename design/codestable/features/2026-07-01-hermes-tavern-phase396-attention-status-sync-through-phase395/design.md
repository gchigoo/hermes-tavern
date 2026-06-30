---
doc_type: feature-design
feature: 2026-07-01-hermes-tavern-phase396-attention-status-sync-through-phase395
title: "Phase 396 attention/status sync through Phase 395"
status: approved
implementation_ready: true
date: "2026-07-01"
owner: standard_lane
lane: standard/personal
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 396 attention/status sync through accepted Phase 395; executor implementation and parent verification remain non-final."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase396, standard-lane]
---

# Phase 396 attention/status sync through Phase 395

## Background / Current Status Evidence

Phase 396 is the correct next bounded CodeStable slice.

Read-only architect evidence:

- Git is on `main` at `9dbb0f5`; `git status --short --branch` reports `## main...origin/main`, and porcelain status reports no changed paths.
- `design/codestable/attention.md` has exactly one current-status line, currently synced through `All phases 1-395 accepted`.
- Phase 395 artifacts are complete and accepted under `design/codestable/features/2026-07-01-hermes-tavern-phase395-attention-status-sync-through-phase394/`.
- `tests/test_hermes_tavern_codestable_status.py` is pinned to Phase 395: current/stale constants are 395/394, live range is `range(168, 396)`, aggregate string is `"range(168, 396)"`, and the split stale guard reaches `stale_aggregate_range_395`.
- `Phase 121-167` and explicit Phase 168 through Phase 395 labels are present.
- No Phase 396 feature directory exists at architect read time.

## Goals

- Materialize the Phase 396 design/checklist pair for a standard/personal S1 handoff slice.
- Advance `design/codestable/attention.md` exactly one status tick from 1-395 to 1-396.
- Append `Phase 396 attention status sync through Phase 395` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 395 label.
- Update the focused status regression to guard the Phase 396 live status contract.
- Keep S1 non-final: leave `acceptance.md` absent and reserve final acceptance/status closeout for the parent controller.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No root-design, README, architecture, roadmap, requirements, compound, build, or cache changes.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes by executor.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction policy change, RP compatibility change, minors-related work, or CSAM-related work.
- No Phase 397 or later work.
- No S2 closeout by executor.
- No `acceptance.md` during S1.

## Allowed Files

Executor S1 may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-01-hermes-tavern-phase396-attention-status-sync-through-phase395/design.md`
- `design/codestable/features/2026-07-01-hermes-tavern-phase396-attention-status-sync-through-phase395/checklist.yaml`

No `acceptance.md` is allowed for this S1 handoff.

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-395 accepted` to `Current status (2026-06-18): All phases 1-396 accepted`.
- Append exactly once in the attention status line: `Phase 396 attention status sync through Phase 395`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 395 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes exactly: `Phase 394 attention status sync through Phase 393, Phase 395 attention status sync through Phase 394, and Phase 396 attention status sync through Phase 395.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-396 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-395 accepted"`
- `STALE_PHASE_MARKER = "1-395"`
- `STALE_PHASE_MARKER_EN_DASH = "1–395"`
- Append `"Phase 396 attention status sync through Phase 395"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 395 required label.
- `FINAL_STATUS_SUFFIX = "Phase 394 attention status sync through Phase 393, Phase 395 attention status sync through Phase 394, and Phase 396 attention status sync through Phase 395."`
- `phase_range = range(168, 397)`
- `aggregate_range = "range(168, 397)"`
- Add `stale_aggregate_range_396 = "".join(["range(168, ", "39", "6", ")"])`.
- Include `stale_aggregate_range_396` in the stale assertion tuple.
- Preserve prior split stale guards, including `stale_aggregate_range_395` and earlier.
- Replace the final split `stale_aggregate_guard` so it builds stale `range(168, 396)` without embedding contiguous `range(168, 396)` in the test source.
- Do not leave a contiguous stale literal `range(168, 396)` in the test source after the update; the live range is `range(168, 397)`.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive substring counts.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Preserve split no-discovery-token guards against `.glob`, `.rglob`, `iterdir`, and `os.walk`.
- Newest-label exact-once applies to the attention status line only. Do not require exact once across the test source because the newest label appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Static Guard Requirements

Controller verification must reject the implementation unless all changed/untracked paths are exactly the four allowed S1 paths listed above before acceptance closeout, `acceptance.md` is absent during S1, and no runtime/source/plugin/provider/gateway/CLI/config/dependency/root-design/README/architecture/roadmap/requirements/compound/build/cache path changed.

Static checks must verify the exact current-status prefix, stale prefix, stale hyphen/en-dash markers, final suffix, preservation of `Phase 121-167`, preservation of every explicit Phase 168 through Phase 395 label, append of Phase 396 exactly once in the attention status line, current-status section placement, anchored assignment-count guards, no direct stale `range(168, 396)` literal in the focused test source except the live aggregate range is `range(168, 397)`, no discovery tokens, final newlines, and no trailing whitespace.

## Structure Health / Microrefactor Decision

No microrefactor is part of this slice. The only planned work is a bounded status-line update, a focused static regression update, and creation of the selected Phase 396 feature artifacts. Changing runtime structure, plugin/provider boundaries, root design, architecture, roadmap, requirements, or compound documents would be outside scope.

## Verification Commands

Parent/controller verification after S1 should run:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase396-attention-status-sync-through-phase395/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase396-attention-status-sync-through-phase395/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static Phase 396 status/scope/final-newline/trailing-whitespace guard using changed plus untracked files.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior explicit phase label.
- The terminal `and` must move to Phase 396; Phase 395 should become comma-separated.
- `range(168, 396)` becomes stale and must not remain as a contiguous stale literal in the focused test source.
- Existing split stale guards, especially `stale_aggregate_range_395`, must remain present in the stale tuple.
- Newest-label exact-once applies only to the attention status line, not to the whole test source.
- Accidentally creating `acceptance.md` in S1 would cross the S1/S2 boundary.
- Any runtime, provider, gateway, CLI, config, dependency, build, root-design, README, architecture, roadmap, requirements, compound, safety, minors/CSAM, or provider-bypass change would violate scope.

## S1 Handoff

This design scopes S1 only. Executor should update the allowed docs/test files, leave `acceptance.md` absent, keep checklist/root acceptance statuses non-final with `parent_verification_required: true`, avoid staging/commit/push, avoid marking parent/controller checks final, and hand back to the parent/controller for final verification, acceptance creation, commit, and push.
