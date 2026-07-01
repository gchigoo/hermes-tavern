---
doc_type: feature-design
feature: 2026-07-01-hermes-tavern-phase404-attention-status-sync-through-phase403
title: "Phase 404 attention/status sync through Phase 403"
status: approved
implementation_ready: true
date: "2026-07-01"
owner: company_boost_lane
lane: company-boost/uncommitted
bounded_phase: "docs/static-test/status-only"
summary: "Approved design for Phase 404 attention/status sync through accepted Phase 403; S1 worker handoff only, pending parent verification, with no executor commit or push."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase404, company-boost]
---

# Phase 404 attention/status sync through Phase 403

## Background / Current Status Evidence

Phase 403 is already accepted and complete. The current CodeStable attention status line is synced through `All phases 1-403 accepted`, Phase 403 artifacts are present and accepted, Phase 402 artifacts are accepted, the focused status regression is pinned to the Phase 403 contract, and no Phase 404 feature directory existed before this slice.

Therefore Phase 404 is the next safe bounded CodeStable slice.

## Goals

- Materialize the Phase 404 design/checklist artifact set for an S1 company-boost dirty-tree handoff.
- Advance `design/codestable/attention.md` exactly one status tick from 1-403 to 1-404.
- Append `Phase 404 attention status sync through Phase 403` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 403 label.
- Update the focused status regression to guard the Phase 404 live status contract.
- Record truthful S1 worker evidence while leaving parent/controller verification pending; executor does not stage, commit, or push.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No root-design, README, architecture, roadmap, requirements, compound, review, build, or cache changes.
- No acceptance.md creation during S1.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction policy change, RP compatibility change, minors-related work, or CSAM-related work.
- No parent/controller verification completion inside this executor slice.
- No Phase 405 or later work.

## Allowed Files

Only these files are in scope:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-01-hermes-tavern-phase404-attention-status-sync-through-phase403/design.md`
- `design/codestable/features/2026-07-01-hermes-tavern-phase404-attention-status-sync-through-phase403/checklist.yaml`

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-403 accepted` to `Current status (2026-06-18): All phases 1-404 accepted`.
- Append exactly once in the attention status line: `Phase 404 attention status sync through Phase 403`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 403 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes exactly: `Phase 402 attention status sync through Phase 401, Phase 403 attention status sync through Phase 402, and Phase 404 attention status sync through Phase 403.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-404 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-403 accepted"`
- `STALE_PHASE_MARKER = "1-403"`
- `STALE_PHASE_MARKER_EN_DASH = "1–403"`
- Append `"Phase 404 attention status sync through Phase 403"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 403 required label.
- `FINAL_STATUS_SUFFIX = "Phase 402 attention status sync through Phase 401, Phase 403 attention status sync through Phase 402, and Phase 404 attention status sync through Phase 403."`
- `phase_range = range(168, 405)`
- `aggregate_range = "range(168, 405)"`
- Add `stale_aggregate_range_404 = "".join(["range(168, ", "40", "4", ")"])`.
- Include `stale_aggregate_range_404` in the stale assertion tuple.
- Preserve prior split stale guards, including `stale_aggregate_range_403`, `stale_aggregate_range_402`, `stale_aggregate_range_401`, and earlier.
- Replace the final split `stale_aggregate_guard` so it builds stale `range(168, 404)` without embedding contiguous `range(168, 404)` in the test source.
- Do not leave a contiguous stale literal `range(168, 404)` in the focused test source after the update; the live range is `range(168, 405)`.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive substring counts.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Preserve split no-discovery-token guards against `.glob`, `.rglob`, `iterdir`, and `os.walk`.
- Newest-label exact-once applies to the attention status line only. Do not require exact once across the test source because the newest label appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Static Guard Requirements

Parent/controller verification must reject the implementation unless all changed/untracked paths are exactly the four allowed Phase 404 paths listed above and no runtime/source/plugin/provider/gateway/CLI/config/dependency/root-design/README/architecture/roadmap/requirements/compound/review/build/cache path changed.

Static checks must verify the exact current-status prefix, stale prefix, stale hyphen/en-dash markers, final suffix, preservation of `Phase 121-167`, preservation of every explicit Phase 168 through Phase 403 label, append of Phase 404 exactly once in the attention status line, current-status section placement, anchored assignment-count guards, no direct stale `range(168, 404)` literal in the focused test source, no discovery tokens, no Phase 404 acceptance.md in S1, final newlines, and no trailing whitespace.

## Structure Health / Microrefactor Decision

No microrefactor is part of this slice. The only planned work is a bounded status-line update, a focused static regression update, and creation of the selected Phase 404 feature design/checklist artifacts. Changing runtime structure, plugin/provider boundaries, root design, architecture, roadmap, requirements, compound documents, or acceptance artifacts would be outside scope.

## Verification Commands

Worker-side execution in S1 may run the YAML validators, compile check, focused status pytest, and `git diff --check`; parent/controller verification remains pending after this executor handoff and is responsible for final acceptance decisions.

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior explicit phase label.
- The terminal `and` must move to Phase 404; Phase 403 should become comma-separated.
- `range(168, 404)` becomes stale and must not remain as a contiguous stale literal in the focused test source.
- Existing split stale guards, especially `stale_aggregate_range_403`, must remain present in the stale tuple.
- Newest-label exact-once applies only to the attention status line, not to the whole test source.
- Any runtime, provider, gateway, CLI, config, dependency, build, root-design, README, architecture, roadmap, requirements, compound, safety, minors/CSAM, or provider-bypass change would violate scope.

## Handoff

This design scopes one complete Phase 404 status-sync slice. Executor updates only the allowed docs/test files, performs no staging/commit/push, does not create `acceptance.md`, and leaves parent/controller verification pending before any repository commit, push, or state finalization.
