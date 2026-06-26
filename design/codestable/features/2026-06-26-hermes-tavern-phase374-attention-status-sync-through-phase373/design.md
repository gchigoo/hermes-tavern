---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase374-attention-status-sync-through-phase373
title: "Phase 374 attention status sync through Phase 373"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 374 attention status sync through accepted Phase 373."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase374, company-boost, parent-handoff]
---

# Phase 374 attention status sync through Phase 373

## Background / Current State

Read-only architect inspection confirmed the safe next bounded slice is Phase 374.

Baseline:

- Branch: `main`; HEAD observed at `2da069d`; status output showed no dirty paths before this slice.
- Phase 373 artifacts exist and are accepted, including `acceptance.md`.
- `design/codestable/attention.md` currently says `Current status (2026-06-18): All phases 1-373 accepted`.
- Current terminal suffix is `Phase 371 attention status sync through Phase 370, Phase 372 attention status sync through Phase 371, and Phase 373 attention status sync through Phase 372.`
- `tests/test_hermes_tavern_codestable_status.py` currently pins Phase 373 with `phase_range = range(168, 374)` and live aggregate string `range(168, 374)`.
- The Phase 374 target directory was absent before this S1 materialization.

## Goals

- Advance `design/codestable/attention.md` exactly one status tick from 1-373 to 1-374.
- Append `Phase 374 attention status sync through Phase 373` exactly once.
- Update the focused status regression to guard the Phase 374 live status contract.
- Preserve `Phase 121-167 novel project layer + metadata + JSON export for all entity types`.
- Preserve every explicit Phase 168 through Phase 373 label.
- Keep the current status bullet immediately after the adult-fiction non-negotiable bullet in `### 其他` and before `### Hermes Tavern 凭证约束`.
- Leave S1 non-final, pending parent verification, with no Phase 374 acceptance artifact.

## Non-Goals

- No `acceptance.md` for Phase 374 during S1.
- No Phase 375 or later work.
- No runtime/source/plugin/provider/gateway/core Hermes edits.
- No root docs, architecture, roadmap, requirements, compound, reference, build, cache, package install, service start, stage, commit, push, reset, or branch changes.
- No provider safety behavior, adult-fiction/RP boundary, minors-related behavior, Hermes-native plugin architecture, or SillyTavern asset compatibility changes.

## Allowed Scope

Executor edits are limited to exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase374-attention-status-sync-through-phase373/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase374-attention-status-sync-through-phase373/checklist.yaml`

## Exact Status Contract

`attention.md` target prefix:

`Current status (2026-06-18): All phases 1-374 accepted`

Append this label exactly once:

`Phase 374 attention status sync through Phase 373`

Final status suffix target:

`Phase 372 attention status sync through Phase 371, Phase 373 attention status sync through Phase 372, and Phase 374 attention status sync through Phase 373.`

Focused test constants:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-374 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-373 accepted"`
- `STALE_PHASE_MARKER = "1-373"`
- `STALE_PHASE_MARKER_EN_DASH = "1–373"`
- Append `"Phase 374 attention status sync through Phase 373"` to `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX = "Phase 372 attention status sync through Phase 371, Phase 373 attention status sync through Phase 372, and Phase 374 attention status sync through Phase 373."`
- `phase_range = range(168, 375)`
- Live aggregate string: `"range(168, 375)"`
- Add `stale_aggregate_range_374 = "".join(["range(168, ", "37", "4", ")"])`.
- Include `stale_aggregate_range_374` in the stale tuple.
- Do not leave a contiguous stale literal `range(168, 374)` in the test source except as split pieces.
- Final suffix terminal labels must be Phase 372, Phase 373, and Phase 374 with only one terminal `and` before Phase 374.

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
- S1 executor checks may be completed by the executor after materialization.
- S2 parent/controller verification checks remain pending.

## Verification Gates

Worker/controller lightweight gates for this S1 handoff:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-26-hermes-tavern-phase374-attention-status-sync-through-phase373/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-26-hermes-tavern-phase374-attention-status-sync-through-phase373/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- static status/range/scope guard confirming allowed files only, anchored assignments, complete label preservation, no contiguous stale `range(168, 374)` literal, and no discovery tokens.
- `test ! -e design/codestable/features/2026-06-26-hermes-tavern-phase374-attention-status-sync-through-phase373/acceptance.md`
- `git diff --check`

Parent controller owns final S2 acceptance creation/finalization and may rerun the full `python -m pytest -q` registry before committing.
