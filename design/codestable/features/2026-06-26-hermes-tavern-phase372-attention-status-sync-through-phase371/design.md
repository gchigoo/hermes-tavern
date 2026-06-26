---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase372-attention-status-sync-through-phase371
title: "Phase 372 attention status sync through Phase 371"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 372 attention status sync through accepted Phase 371."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase372, company-boost, parent-handoff]
---

# Phase 372 attention status sync through Phase 371

## Background / Current State

Read-only architect inspection confirmed the safe next bounded slice is Phase 372.

Baseline:

- Branch: `main`; controller reported a clean tree before this architect pass.
- Phase 371 artifacts exist and are accepted, including `acceptance.md`.
- `design/codestable/attention.md` currently says `Current status (2026-06-18): All phases 1-371 accepted`.
- Current terminal suffix is `Phase 369 attention status sync through Phase 368, Phase 370 attention status sync through Phase 369, and Phase 371 attention status sync through Phase 370.`
- `tests/test_hermes_tavern_codestable_status.py` currently pins Phase 371 with `phase_range = range(168, 372)` and live aggregate string `range(168, 372)`.

## Goals

- Advance `design/codestable/attention.md` exactly one status tick from 1-371 to 1-372.
- Append `Phase 372 attention status sync through Phase 371` exactly once.
- Update the focused status regression to guard the Phase 372 live status contract.
- Preserve `Phase 121-167 novel project layer + metadata + JSON export for all entity types`.
- Preserve every explicit Phase 168 through Phase 371 label.
- Keep the current status bullet immediately after the adult-fiction non-negotiable bullet in `### 其他` and before `### Hermes Tavern 凭证约束`.
- Leave S1 non-final, pending parent verification, with no Phase 372 acceptance artifact.

## Non-Goals

- No `acceptance.md` for Phase 372.
- No Phase 373 or later work.
- No runtime/source/plugin/provider/gateway/core Hermes edits.
- No root docs, architecture, roadmap, requirements, compound, reference, build, cache, package install, service start, stage, commit, push, reset, or branch changes.

## Allowed Scope

Executor edits are limited to exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase372-attention-status-sync-through-phase371/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase372-attention-status-sync-through-phase371/checklist.yaml`

## Exact Status Contract

`attention.md` target prefix:

`Current status (2026-06-18): All phases 1-372 accepted`

Final status suffix target:

`Phase 370 attention status sync through Phase 369, Phase 371 attention status sync through Phase 370, and Phase 372 attention status sync through Phase 371.`

Focused test constants:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-372 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-371 accepted"`
- `STALE_PHASE_MARKER = "1-371"`
- `STALE_PHASE_MARKER_EN_DASH = "1–371"`
- Append `"Phase 372 attention status sync through Phase 371"` to `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 370 attention status sync through Phase 369, Phase 371 attention status sync through Phase 370, and Phase 372 attention status sync through Phase 371."`
- `phase_range = range(168, 373)`
- Live aggregate string: `"range(168, 373)"`
- Add `stale_aggregate_range_372 = "".join(["range(168, ", "37", "2", ")"])`.
- Include `stale_aggregate_range_372` in the stale tuple.
- Do not leave contiguous stale literal `range(168, 372)` in the test source.

## Checklist State After S1

After executor S1:

- checklist root `status: implemented`
- `workflow_status: pending_parent_verification`
- `acceptance_state: pending_parent_verification`
- `parent_verification_required: true`
- `worker_commit_or_push_performed: false`
- `acceptance_artifact: null`
- S1 checks completed
- S2 checks pending
