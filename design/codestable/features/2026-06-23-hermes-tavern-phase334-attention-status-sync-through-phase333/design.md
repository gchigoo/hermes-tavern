---
doc_type: feature-design
status: planned
workflow_status: planned
feature: 2026-06-23-hermes-tavern-phase334-attention-status-sync-through-phase333
date: "2026-06-23"
owner: company_boost_lane
lane: company-boost/parent-verified-artifact
bounded_phase: "docs/static-test/status-only"
implementation_ready: false
result_type: planning_only
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase334]
summary: "Artifact-only planning contract for Phase 334 status-sync work through Phase 333."
---

# Phase 334: Attention Status Sync Through Phase 333

## Gate

- Prior phase acceptance exists at `design/codestable/features/2026-06-23-hermes-tavern-phase333-attention-status-sync-through-phase332/acceptance.md`.
- Phase 333 checklist and acceptance are already accepted; live `attention.md` and the focused status test are synced through Phase 333.
- No Phase 334 feature directory existed before this planning-only slice.
- This slice is explicitly artifact-only and **does not** advance live status lines or focused tests.

## Goals

- Define the future Phase 334 attention/status-sync contract.
- Preserve current live status at Phase 333 during this slice.
- Materialize only two planning artifacts:
  - `design/codestable/features/2026-06-23-hermes-tavern-phase334-attention-status-sync-through-phase333/design.md`
  - `design/codestable/features/2026-06-23-hermes-tavern-phase334-attention-status-sync-through-phase333/checklist.yaml`
- Keep the next executor/parent-controller handoff clear without claiming implementation, acceptance, commit, or push.

## Non-Goals

- No `acceptance.md` for Phase 334 in this slice.
- No edits to `design/codestable/attention.md`.
- No edits to `tests/test_hermes_tavern_codestable_status.py`.
- No runtime/source/plugin/provider/gateway/CLI/config/dependency/root-doc work.
- No minors-related work and no provider-safety bypass.

## Exact Future Status Contract

When a later approved implementation/closeout slice advances Phase 334, it should apply these values:

- eventual attention prefix:
  - `Current status (2026-06-18): All phases 1-334 accepted`
- eventual attention label:
  - `Phase 334 attention status sync through Phase 333`
- future stale prefix/markers:
  - `Current status (2026-06-18): All phases 1-333 accepted`
  - `1-333`
  - `1–333`
- future `phase_range`:
  - `range(168, 335)`
- future `aggregate_range`:
  - `range(168, 335)`
- future split stale guard:
  - `range(168, 334)`

## Current Live Status Must Remain

For this planning-only slice, live files must remain at the Phase 333 contract:

- `design/codestable/attention.md` prefix stays:
  - `Current status (2026-06-18): All phases 1-333 accepted`
- Terminal live label remains:
  - `Phase 333 attention status sync through Phase 332`
- `tests/test_hermes_tavern_codestable_status.py` remains at:
  - `phase_range = range(168, 334)`
  - `aggregate_range = "range(168, 334)"`
  - split stale guard for `range(168, 333)`

## Allowed Files For This Slice

Exactly these new planning files are allowed:

- `design/codestable/features/2026-06-23-hermes-tavern-phase334-attention-status-sync-through-phase333/design.md`
- `design/codestable/features/2026-06-23-hermes-tavern-phase334-attention-status-sync-through-phase333/checklist.yaml`

## Future Implementation Scope

If a later separately approved slice implements Phase 334 closeout, it may update the live attention/status contract and focused test according to the future values above, then create acceptance evidence. That is intentionally out of scope here.

## Prohibited Scope

The following remain prohibited for this slice:

- `run_agent.py`, `cli.py`, and `gateway/run.py`
- runtime, source, plugin, provider, gateway, config, and dependency files
- root README and root design docs
- `design/codestable/architecture`, `design/codestable/roadmap`, `design/codestable/requirements`, `design/codestable/compound`, and build docs
- discovery-token broadening via `.glob(`, `.rglob(`, `.iterdir(`, or `os.walk`
- service lifecycle commands
- commits, pushes, staging, or release/deploy work
- minors-related work or provider-safety bypasses

This slice preserves Hermes-native plugin architecture and SillyTavern asset compatibility.

## Verification Criteria

- `validate-yaml.py` passes for this feature directory with required `doc_type`, `status`, and `feature` metadata.
- `git status --short --untracked-files=all` shows exactly the two Phase 334 planning artifacts as dirty/untracked.
- `git diff --check` passes.
- A static guard confirms no `acceptance.md`, no live status/test changes, no protected-scope changes, and no trailing whitespace/missing final newlines in the new files.
- Full pytest may be left to the parent controller for this planning-only slice because no runtime or tests are changed.

## Executor Instructions

Executor may be skipped for this `planning_only` result. If policy requires an executor pass, it must be restricted to materializing only `design.md` and `checklist.yaml` from this approved contract. It must not create `acceptance.md`, advance `attention.md`, edit the focused status test, touch runtime/source/plugin/provider/gateway/CLI/config/dependency files, run service lifecycle commands, commit, or push.
