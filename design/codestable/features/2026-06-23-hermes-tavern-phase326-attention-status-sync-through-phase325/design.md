---
doc_type: feature-design
status: approved
feature: "2026-06-23-hermes-tavern-phase326-attention-status-sync-through-phase325"
date: "2026-06-23"
owner: standard_lane
lane: "standard/personal"
implementation_ready: true
parent_verification_required: true
bounded_phase: "docs/static-test/status-only"
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase326]
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 325 only, without changing runtime behavior.
---

# Phase 326: CodeStable Attention Status Sync Through Phase 325

## Gate

Phase 325 is accepted at `design/codestable/features/2026-06-23-hermes-tavern-phase325-attention-status-sync-through-phase324/acceptance.md`.

Current state before this slice:
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-325 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` enforces the Phase 325 prefix, required labels through Phase 325, `phase_range = range(168, 326)`, and `aggregate_range = "range(168, 326)"`.
- No `phase326` feature directory exists in the inspected feature set.
- No higher-confidence unfinished planned/draft/in-progress feature artifact was found in the top-level feature scan.
- `design/codestable/roadmap/` does not exist, so there is no roadmap item to preempt this recurring status-only slice.

Selected slice: recurring status-only Phase 326 sync through accepted Phase 325.

## Goals

- Advance exactly one recurring status-sync phase: Phase 326 syncs through accepted Phase 325 only.
- Update only `attention.md`, the focused static status test, and the new Phase 326 feature artifact directory.
- Preserve Hermes-native plugin architecture, SillyTavern asset compatibility, and all runtime behavior.
- Keep the slice adult-fiction/RP compatible by making no content-policy, persona, safety-bypass, or minor-related changes.

## Non-Goals

- Do not touch runtime/source/plugin/provider/gateway/CLI files, root design, README, architecture, requirements, compound docs, assets, fixtures, schemas, dependency/config/build files, or service lifecycle behavior.
- Do not change model/provider routing, credentials, provider safety behavior, network behavior, dependency files, or configuration files.
- Do not add a Phase 327 attention/status label.
- Do not edit existing prior phase feature directories.
- Do not finalize checklist/acceptance from executor S1, stage, commit, push, send messages, update progress state, or perform broad rewrites.

## Exact Status Contract

Change the `attention.md` current-status prefix:
- From: `Current status (2026-06-18): All phases 1-325 accepted`
- To: `Current status (2026-06-18): All phases 1-326 accepted`

Append exactly once after `Phase 325 attention status sync through Phase 324`:
- Convert `Phase 324 attention status sync through Phase 323, and Phase 325 attention status sync through Phase 324.`
- To `Phase 324 attention status sync through Phase 323, Phase 325 attention status sync through Phase 324, and Phase 326 attention status sync through Phase 325.`

Preserve:
- `Phase 121-167`
- Every explicit `Phase 168` through `Phase 325` short label exactly as already written.

Do not add:
- Any `Phase 327` attention/status label.

Final attention suffix must end with:
`Phase 324 attention status sync through Phase 323, Phase 325 attention status sync through Phase 324, and Phase 326 attention status sync through Phase 325.`

Full focused-test suffix must become exactly:
`Phase 305 attention status sync through Phase 304, Phase 306 attention status sync through Phase 305, Phase 307 attention status sync through Phase 306, Phase 308 attention status sync through Phase 307, Phase 309 attention status sync through Phase 308, Phase 310 attention status sync through Phase 309, Phase 311 attention status sync through Phase 310, Phase 312 attention status sync through Phase 311, Phase 313 attention status sync through Phase 312, Phase 314 attention status sync through Phase 313, Phase 315 attention status sync through Phase 314, Phase 316 attention status sync through Phase 315, Phase 317 attention status sync through Phase 316, Phase 318 attention status sync through Phase 317, Phase 319 attention status sync through Phase 318, Phase 320 attention status sync through Phase 319, Phase 321 attention status sync through Phase 320, Phase 322 attention status sync through Phase 321, Phase 323 attention status sync through Phase 322, Phase 324 attention status sync through Phase 323, Phase 325 attention status sync through Phase 324, and Phase 326 attention status sync through Phase 325.`

## Focused Test Contract

Update `tests/test_hermes_tavern_codestable_status.py`:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-326 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-325 accepted"`
- `STALE_PHASE_MARKER = "1-325"`
- `STALE_PHASE_MARKER_EN_DASH = "1–325"`
- Append `Phase 326 attention status sync through Phase 325` to `REQUIRED_PHASE_LABELS` exactly once.
- Preserve every existing required label through Phase 325.
- `FINAL_STATUS_SUFFIX` equals the Phase 305 through Phase 326 suffix above, with final punctuation and only one final `and` before Phase 326.
- Runtime `phase_range` becomes `range(168, 327)`.
- Source self-check literal becomes `aggregate_range = "range(168, 327)"`.
- Add split stale aggregate guard for `range(168, 326)`.
- Retain older split stale aggregate guards, including `range(168, 325)`, `range(168, 324)`, `range(168, 323)`, `range(168, 322)`, `range(168, 321)`, `range(168, 320)`, `range(168, 319)`, and `range(168, 318)`.
- Preserve the anchored single `CURRENT_STATUS_PREFIX` assignment guard.
- Preserve no-discovery-token guards: no `.glob(`, `.rglob(`, `iterdir(`, or `os.walk` tokens in focused test source.

## Allowed Files

Executor S1 may edit only:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

Parent controller may materialize/finalize only:
- `design/codestable/features/2026-06-23-hermes-tavern-phase326-attention-status-sync-through-phase325/design.md`
- `design/codestable/features/2026-06-23-hermes-tavern-phase326-attention-status-sync-through-phase325/checklist.yaml`
- `design/codestable/features/2026-06-23-hermes-tavern-phase326-attention-status-sync-through-phase325/acceptance.md`

## Prohibited Files and Actions

Protected/prohibited: `run_agent.py`, `cli.py`, `gateway/run.py`, runtime/source/plugin/provider/gateway/CLI files, `plugins/`, provider files, gateway files, plugin runtime files, credentials, root design, README, architecture, roadmap, requirements, compound docs, assets, fixtures, schemas, build outputs, dependency/config files, provider/model/network behavior, SillyTavern asset compatibility behavior, RP content-policy behavior, minor-related features, service lifecycle commands, edits to prior phase directories, broad rewrites, executor staging, executor commit/push, executor messages, progress-state updates, and executor checklist/acceptance finalization.

## Structure Health

This is a docs/static-test/status-only slice. It changes one mandatory startup bullet and one focused static regression. No new executor files are added. A refactor would increase risk and exceed the bounded slice.

## Implementation Steps

S1: Executor status sync only.
- Update `attention.md` prefix and append only the Phase 326 label.
- Update only focused test constants, required label, suffix, phase range, aggregate range, stale markers, stale split aggregate guards, and preserved static guards.
- Do not finalize checklist or acceptance.

S2: Parent verification and artifact-only closeout.
- Run required validation commands.
- Confirm changed/untracked paths stay inside the allowed lists.
- Finalize only Phase 326 feature artifacts after verification.
- If any gate fails, leave status non-final and report the first concrete mismatch.
