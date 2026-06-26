---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase373-attention-status-sync-through-phase372
title: "Phase 373 attention status sync through Phase 372"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 373 attention status sync through accepted Phase 372."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase373, company-boost, parent-handoff]
---

# Phase 373 attention status sync through Phase 372

## Background / Current State

Read-only architect inspection confirmed the safe next bounded slice is Phase 373.

Baseline:

- Branch: `main`; HEAD observed at `3d2cc60`; status output showed no dirty paths.
- Phase 372 artifacts exist and are accepted, including `acceptance.md`.
- `design/codestable/attention.md` currently says `Current status (2026-06-18): All phases 1-372 accepted`.
- Current terminal suffix is `Phase 370 attention status sync through Phase 369, Phase 371 attention status sync through Phase 370, and Phase 372 attention status sync through Phase 371.`
- `tests/test_hermes_tavern_codestable_status.py` currently pins Phase 372 with `phase_range = range(168, 373)` and live aggregate string `range(168, 373)`.

## Goals

- Advance `design/codestable/attention.md` exactly one status tick from 1-372 to 1-373.
- Append `Phase 373 attention status sync through Phase 372` exactly once.
- Update the focused status regression to guard the Phase 373 live status contract.
- Preserve `Phase 121-167 novel project layer + metadata + JSON export for all entity types`.
- Preserve every explicit Phase 168 through Phase 372 label.
- Keep the current status bullet immediately after the adult-fiction non-negotiable bullet in `### 其他` and before `### Hermes Tavern 凭证约束`.
- Leave S1 non-final, pending parent verification, with no Phase 373 acceptance artifact.

## Non-Goals

- No `acceptance.md` for Phase 373 during S1.
- No Phase 374 or later work.
- No runtime/source/plugin/provider/gateway/core Hermes edits.
- No root docs, architecture, roadmap, requirements, compound, reference, build, cache, package install, service start, stage, commit, push, reset, or branch changes.
- No provider safety behavior, adult-fiction/RP boundary, minors-related behavior, Hermes-native plugin architecture, or SillyTavern asset compatibility changes.

## Allowed Scope

Executor edits are limited to exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase373-attention-status-sync-through-phase372/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase373-attention-status-sync-through-phase372/checklist.yaml`

## Exact Status Contract

`attention.md` target prefix:

`Current status (2026-06-18): All phases 1-373 accepted`

Append this label exactly once:

`Phase 373 attention status sync through Phase 372`

Final status suffix target:

`Phase 371 attention status sync through Phase 370, Phase 372 attention status sync through Phase 371, and Phase 373 attention status sync through Phase 372.`

Focused test constants:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-373 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-372 accepted"`
- `STALE_PHASE_MARKER = "1-372"`
- `STALE_PHASE_MARKER_EN_DASH = "1–372"`
- Append `"Phase 373 attention status sync through Phase 372"` to `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 371 attention status sync through Phase 370, Phase 372 attention status sync through Phase 371, and Phase 373 attention status sync through Phase 372."`
- `phase_range = range(168, 374)`
- Live aggregate string: `"range(168, 374)"`
- Add `stale_aggregate_range_373 = "".join(["range(168, ", "37", "3", ")"])`.
- Include `stale_aggregate_range_373` in the stale tuple.
- Do not leave a contiguous stale literal `range(168, 373)` in the test source except as split pieces.
- Final suffix terminal labels must be Phase 371, Phase 372, and Phase 373 with only one terminal `and` before Phase 373.

## Checklist State After S1

After executor S1:

- checklist root `status: implemented`
- `workflow_status: pending_parent_verification`
- `acceptance_state: pending_parent_verification`
- `implementation_ready: true`
- `parent_verification_required: true`
- `worker_commit_or_push_performed: false`
- `parent_commit_or_push_performed: false`
- `acceptance_artifact: null`
- S1 executor checks are planned in this read-only contract and may be completed by the executor after materialization.
- S2 parent/controller verification checks remain pending.
