---
doc_type: feature-design
status: approved
feature: "2026-06-23-hermes-tavern-phase330-attention-status-sync-through-phase329"
date: "2026-06-23"
owner: company_boost_lane
lane: "company-boost/uncommitted"
implementation_ready: true
parent_verification_required: true
bounded_phase: "docs/static-test/status-only"
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase330]
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 329 only, without changing runtime behavior.
---

# Phase 330: CodeStable Attention Status Sync Through Phase 329

## Gate

Phase 329 is accepted at `design/codestable/features/2026-06-23-hermes-tavern-phase329-attention-status-sync-through-phase328/acceptance.md`.

Current state before this slice:
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-329 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` enforces the Phase 329 prefix, required labels through Phase 329, `phase_range = range(168, 330)`, and `aggregate_range = "range(168, 330)"`.
- No `phase330` feature directory existed before this controller materialization.

Selected slice: recurring status-only Phase 330 sync through accepted Phase 329.

## Goals

- Advance exactly one recurring status-sync phase: Phase 330 syncs through accepted Phase 329 only.
- Update only `attention.md`, the focused static status test, and this Phase 330 feature artifact directory.
- Preserve Hermes-native plugin architecture, SillyTavern asset compatibility, and all runtime behavior.
- Keep adult-fiction/RP compatibility while making no content-policy, safety-bypass, or minor-related changes.
- Leave final acceptance/status closeout to the parent controller.

## Non-Goals

- Do not touch runtime/source/plugin/provider/gateway/CLI files, root design, README, architecture, requirements, roadmap, compound docs, assets, fixtures, schemas, dependency/config/build files, or service lifecycle behavior.
- Do not change model/provider routing, credentials, provider safety behavior, network behavior, dependency files, or configuration files.
- Do not add a Phase 331 attention/status label.
- Do not edit existing prior phase feature directories.
- Do not create `acceptance.md`, finalize acceptance, stage, commit, push, send messages, update progress state, or perform broad rewrites.

## Exact Status Contract

Change the `attention.md` current-status prefix:
- From: `Current status (2026-06-18): All phases 1-329 accepted`
- To: `Current status (2026-06-18): All phases 1-330 accepted`

Append exactly once after `Phase 329 attention status sync through Phase 328`:
- Convert `Phase 328 attention status sync through Phase 327, and Phase 329 attention status sync through Phase 328.`
- To `Phase 328 attention status sync through Phase 327, Phase 329 attention status sync through Phase 328, and Phase 330 attention status sync through Phase 329.`

Preserve:
- `Phase 121-167`
- Every explicit `Phase 168` through `Phase 329` short label exactly as already written.

Do not add:
- Any `Phase 331` attention/status label.

Final attention suffix must end with:
`Phase 328 attention status sync through Phase 327, Phase 329 attention status sync through Phase 328, and Phase 330 attention status sync through Phase 329.`

Full focused-test suffix must become exactly:
`Phase 307 attention status sync through Phase 306, Phase 308 attention status sync through Phase 307, Phase 309 attention status sync through Phase 308, Phase 310 attention status sync through Phase 309, Phase 311 attention status sync through Phase 310, Phase 312 attention status sync through Phase 311, Phase 313 attention status sync through Phase 312, Phase 314 attention status sync through Phase 313, Phase 315 attention status sync through Phase 314, Phase 316 attention status sync through Phase 315, Phase 317 attention status sync through Phase 316, Phase 318 attention status sync through Phase 317, Phase 319 attention status sync through Phase 318, Phase 320 attention status sync through Phase 319, Phase 321 attention status sync through Phase 320, Phase 322 attention status sync through Phase 321, Phase 323 attention status sync through Phase 322, Phase 324 attention status sync through Phase 323, Phase 325 attention status sync through Phase 324, Phase 326 attention status sync through Phase 325, Phase 327 attention status sync through Phase 326, Phase 328 attention status sync through Phase 327, Phase 329 attention status sync through Phase 328, and Phase 330 attention status sync through Phase 329.`

## Focused Test Contract

Update `tests/test_hermes_tavern_codestable_status.py`:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-330 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-329 accepted"`
- `STALE_PHASE_MARKER = "1-329"`
- `STALE_PHASE_MARKER_EN_DASH = "1–329"`
- Append `Phase 330 attention status sync through Phase 329` to `REQUIRED_PHASE_LABELS` exactly once.
- Preserve every existing required label through Phase 329.
- `FINAL_STATUS_SUFFIX` equals the Phase 307 through Phase 330 suffix above, with final punctuation and only one final `and` before Phase 330.
- Runtime `phase_range` becomes `range(168, 331)`.
- Source self-check literal becomes `aggregate_range = "range(168, 331)"`.
- Add split stale aggregate guard for `range(168, 330)`.
- Retain older split stale aggregate guards, including `range(168, 329)`, `range(168, 328)`, `range(168, 327)`, `range(168, 326)`, `range(168, 325)`, `range(168, 324)`, `range(168, 323)`, `range(168, 322)`, `range(168, 321)`, `range(168, 320)`, `range(168, 319)`, and `range(168, 318)`.
- Preserve the anchored single `CURRENT_STATUS_PREFIX` assignment guard.
- Preserve no-discovery-token guards: no `.glob(`, `.rglob(`, `iterdir(`, or `os.walk` tokens in focused test source.

## Allowed Files

Executor S1 may edit only:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-23-hermes-tavern-phase330-attention-status-sync-through-phase329/design.md`
- `design/codestable/features/2026-06-23-hermes-tavern-phase330-attention-status-sync-through-phase329/checklist.yaml`

No `acceptance.md` should be created during this lane.

## Prohibited Files and Actions

Protected/prohibited: `run_agent.py`, `cli.py`, `gateway/run.py`, runtime/source/plugin/provider/gateway/CLI files, `plugins/`, provider files, gateway files, plugin runtime files, credentials, root design, README, architecture, roadmap, requirements, compound docs, assets, fixtures, schemas, build outputs, dependency/config files, provider/model/network behavior, SillyTavern asset compatibility behavior, RP content-policy behavior, minor-related features, service lifecycle commands, edits to prior phase directories, broad rewrites, staging, commit/push, messages, progress-state updates, and acceptance finalization.

## Structure Health

This is a docs/static-test/status-only slice. It changes one mandatory startup bullet, one focused static regression, and the Phase 330 feature artifacts. No runtime behavior changes and no new executor implementation files are needed. A refactor would increase risk and exceed the bounded slice.

## Executor Prompt

Implement only Phase 330 attention/status sync through Phase 329. Allowed files only:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-23-hermes-tavern-phase330-attention-status-sync-through-phase329/design.md`
- `design/codestable/features/2026-06-23-hermes-tavern-phase330-attention-status-sync-through-phase329/checklist.yaml`

Do not create `acceptance.md`. Do not finalize acceptance, stage, commit, push, run service lifecycle commands, or touch any protected/runtime/source/plugin/provider/gateway/CLI/config/dependency/root-doc/prior-phase path.

Update attention prefix from `Current status (2026-06-18): All phases 1-329 accepted` to `Current status (2026-06-18): All phases 1-330 accepted`; append exactly `Phase 330 attention status sync through Phase 329`; preserve Phase 121-167 and every explicit Phase 168-329 label; no Phase 331 label.

Update focused test constants to Phase 330 current and Phase 329 stale, append the Phase 330 required label exactly once, set `FINAL_STATUS_SUFFIX` to Phase 307 through Phase 330, set `phase_range = range(168, 331)`, set `aggregate_range = "range(168, 331)"`, add split stale aggregate guard for `range(168, 330)`, retain older split stale aggregate guards including 329, 328, and prior, and preserve no-discovery-token and single-current-prefix guards.

Run focused verification if feasible and report results.

## Implementation Steps

S1: Executor status sync only.
- Update `attention.md` prefix and append only the Phase 330 label.
- Update only focused test constants, required label, suffix, phase range, aggregate range, stale markers, stale split aggregate guards, and preserved static guards.
- Keep checklist/statuses non-final for parent verification.
- Do not create acceptance.md.

S2: Parent verification and artifact-only closeout.
- Parent reruns required validation commands.
- Confirm changed/untracked paths stay inside the allowed lists.
- Finalize only after parent-controller verification, if requested by parent.
- If any gate fails, leave status non-final and report the first concrete mismatch.
