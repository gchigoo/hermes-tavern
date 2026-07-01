---
doc_type: feature-design
feature: 2026-07-02-hermes-tavern-phase409-attention-status-sync-through-phase408
title: "Phase 409 attention/status sync through Phase 408"
status: approved
implementation_ready: true
date: "2026-07-02"
owner: standard_lane
lane: standard/personal
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 409 attention/status sync through accepted Phase 408; executor implementation is bounded to startup status docs/tests and parent verification remains non-final until controller closeout."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase409, standard-lane]
---

# Phase 409 attention/status sync through Phase 408

## Background / Current Status Evidence

Phase 408 is accepted and complete. This read-only architect pass inspected `design/codestable/attention.md`, the Phase 408 accepted artifacts, and `tests/test_hermes_tavern_codestable_status.py`, then selected Phase 409 as the next safe bounded CodeStable slice.

Current evidence before S1:

- `design/codestable/attention.md` is the startup attention source of truth and is synced through `All phases 1-408 accepted`.
- Phase 408 artifacts are complete and accepted under `design/codestable/features/2026-07-01-hermes-tavern-phase408-attention-status-sync-through-phase407/`.
- The focused status regression is pinned to the Phase 408 live contract.
- No Phase 409 artifact existed before the architect pass.

## Goals

- Materialize the Phase 409 design/checklist pair for a standard/personal S1 handoff slice.
- Advance `design/codestable/attention.md` exactly one status tick from 1-408 to 1-409.
- Append `Phase 409 attention status sync through Phase 408` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 408 label.
- Update the focused status regression to guard the Phase 409 live status contract.
- Keep S1 non-final: leave `acceptance.md` absent and reserve final acceptance/status closeout for the parent controller.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No build, root-design, README, architecture, roadmap, requirements, compound, review, or cache changes.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes by executor.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction boundary change, RP compatibility change, minors-related work, or CSAM-related work.
- No Phase 410 or later work.
- No S2 closeout by executor.
- No `acceptance.md` during S1.
- No final checklist, workflow, or acceptance statuses during S1.

## Allowed Files

Executor S1 may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-02-hermes-tavern-phase409-attention-status-sync-through-phase408/design.md`
- `design/codestable/features/2026-07-02-hermes-tavern-phase409-attention-status-sync-through-phase408/checklist.yaml`

No `acceptance.md` is allowed for this S1 handoff.

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-408 accepted` to `Current status (2026-06-18): All phases 1-409 accepted`.
- Append exactly once in the attention status line: `Phase 409 attention status sync through Phase 408`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 408 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes exactly: `Phase 407 attention status sync through Phase 406, Phase 408 attention status sync through Phase 407, and Phase 409 attention status sync through Phase 408.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-409 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-408 accepted"`
- `STALE_PHASE_MARKER = "1-408"`
- `STALE_PHASE_MARKER_EN_DASH = "1–408"`
- Append `"Phase 409 attention status sync through Phase 408"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 408 required label.
- `FINAL_STATUS_SUFFIX = "Phase 407 attention status sync through Phase 406, Phase 408 attention status sync through Phase 407, and Phase 409 attention status sync through Phase 408."`
- `phase_range = range(168, 410)`
- `aggregate_range = "range(168, 410)"`
- Add `stale_aggregate_range_409 = "".join(["range(168, ", "40", "9", ")"])`.
- Include `stale_aggregate_range_409` in the stale assertion tuple.
- Preserve prior split stale guards, including `stale_aggregate_range_408` and earlier.
- Replace the final split `stale_aggregate_guard` so it builds stale `range(168, 409)` without embedding contiguous `range(168, 409)` in the test source.
- Do not leave a contiguous stale literal `range(168, 409)` in the test source after the update; the live range is `range(168, 410)`.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive substring counts.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Preserve split no-discovery-token guards against `.glob`, `.rglob`, `iterdir`, and `os.walk`.
- Newest-label exact-once applies to the attention status line only. Do not require exact once across the test source because the newest label appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Static Guard Requirements

Controller verification must reject the implementation unless all changed/untracked paths are exactly the four allowed S1 paths listed above before acceptance closeout, `acceptance.md` is absent during S1, and no runtime/source/plugin/provider/gateway/CLI/config/dependency/build/root-design/README/architecture/roadmap/requirements/compound/review/cache path changed.

Static checks must verify the exact current-status prefix, stale prefix, stale hyphen/en-dash markers, final suffix, preservation of `Phase 121-167`, preservation of every explicit Phase 168 through Phase 408 label, append of Phase 409 exactly once in the attention status line, current-status section placement, anchored assignment-count guards, no direct stale `range(168, 409)` literal in the focused test source, no discovery tokens, final newline, and no trailing whitespace.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-02-hermes-tavern-phase409-attention-status-sync-through-phase408/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-02-hermes-tavern-phase409-attention-status-sync-through-phase408/checklist.yaml --yaml-only`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase409-executor python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static Phase 409 S1 scope/status/final-newline/trailing-whitespace guard using changed plus untracked files.
- Parent-owned broader pytest gate when feasible: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='`
- `git diff --check`

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior explicit phase label.
- The terminal `and` must move to Phase 409; Phase 408 should become comma-separated.
- `range(168, 409)` becomes stale and must not remain as a contiguous stale literal in the focused test source.
- Existing split stale guards, especially `stale_aggregate_range_408`, must remain present in the stale tuple.
- Newest-label exact-once applies only to the attention status line, not to the whole test source.
- Accidentally creating `acceptance.md` or marking final statuses in S1 would cross the S1/S2 boundary.
- Any runtime, source, plugin, provider, gateway, CLI, config, dependency, build, root-design, README, architecture, roadmap, requirements, compound, review, cache, safety, minors/CSAM, or provider-bypass change would violate scope.

## Handoff

This design scopes one complete Phase 409 S1 status-sync slice. Executor updates only the allowed docs/test files, performs no staging/commit/push, does not create `acceptance.md`, does not mark final statuses, and leaves parent/controller verification pending before any repository commit, push, or state finalization.
