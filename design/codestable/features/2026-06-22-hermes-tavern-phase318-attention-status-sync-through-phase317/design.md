---
doc_type: feature-design
status: approved
feature: "2026-06-22-hermes-tavern-phase318-attention-status-sync-through-phase317"
date: "2026-06-22"
owner: standard_lane
lane: "standard/personal"
implementation_ready: true
parent_verification_required: true
bounded_phase: "docs/static-test/status-only"
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase318]
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 317 only, without changing runtime behavior.
---

# Phase 318: CodeStable Attention Status Sync Through Phase 317

## Gate

Phase 317 is accepted at `design/codestable/features/2026-06-22-hermes-tavern-phase317-attention-status-sync-through-phase316/acceptance.md`.

Current state before this slice:
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-317 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` enforces the Phase 317 prefix, required labels through Phase 317, `phase_range = range(168, 318)`, and `aggregate_range = "range(168, 318)"`.
- No Phase 318 status-sync feature directory existed before this controller materialization.

## Goals

- Advance exactly one recurring status-sync phase: Phase 318 syncs through accepted Phase 317 only.
- Update only `attention.md`, the focused static status test, and this Phase 318 feature artifact directory.
- Preserve Hermes-native plugin architecture and SillyTavern asset compatibility by avoiding all runtime and asset changes.
- Keep adult-fiction/RP compatibility unchanged; do not involve minors or bypass provider safety systems.
- Leave verification, checklist finalization, acceptance finalization, staging, commit, push, messages, service lifecycle commands, and progress-state updates to the parent controller or outside this executor slice.

## Non-Goals

- Do not touch runtime/source/plugin/provider/gateway/CLI files, root design, README, architecture, roadmap, requirements, compound docs, assets, fixtures, schemas, dependency/config/build files, or service lifecycle behavior.
- Do not change model/provider routing, credentials, adult-fiction/RP compatibility, provider safety behavior, network behavior, dependency files, or configuration files.
- Do not add a Phase 319 attention/status label; this slice records Phase 318 as the newly accepted completed phase.
- Do not edit existing prior phase feature directories.
- Do not let the executor finalize checklist/acceptance, stage, commit, push, send messages, update progress state, or perform broad rewrites.

This lane is docs/static-test/status-only. Hermes-native plugin architecture, SillyTavern asset compatibility, and provider/runtime behavior are unaffected and must remain untouched.

## Exact Status Contract

Change the `attention.md` current-status prefix:
- From: `Current status (2026-06-18): All phases 1-317 accepted`
- To: `Current status (2026-06-18): All phases 1-318 accepted`

Append exactly once after `Phase 317 attention status sync through Phase 316`:
- Convert `and Phase 317 attention status sync through Phase 316.`
- To `Phase 317 attention status sync through Phase 316, and Phase 318 attention status sync through Phase 317.`

Preserve:
- `Phase 121-167`
- Every explicit `Phase 168` through `Phase 317` short label exactly as already written.

Do not add:
- Any `Phase 319` attention/status label to `attention.md` or the focused status label list.

Final suffix must become exactly:
`Phase 303 attention status sync through Phase 302, Phase 304 attention status sync through Phase 303, Phase 305 attention status sync through Phase 304, Phase 306 attention status sync through Phase 305, Phase 307 attention status sync through Phase 306, Phase 308 attention status sync through Phase 307, Phase 309 attention status sync through Phase 308, Phase 310 attention status sync through Phase 309, Phase 311 attention status sync through Phase 310, Phase 312 attention status sync through Phase 311, Phase 313 attention status sync through Phase 312, Phase 314 attention status sync through Phase 313, Phase 315 attention status sync through Phase 314, Phase 316 attention status sync through Phase 315, Phase 317 attention status sync through Phase 316, and Phase 318 attention status sync through Phase 317.`

## Focused Test Contract

Update `tests/test_hermes_tavern_codestable_status.py`:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-318 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-317 accepted"`
- `STALE_PHASE_MARKER = "1-317"`
- `STALE_PHASE_MARKER_EN_DASH = "1–317"`
- Append `Phase 318 attention status sync through Phase 317` to `REQUIRED_PHASE_LABELS` exactly once.
- Preserve every existing required label through Phase 317.
- `FINAL_STATUS_SUFFIX` equals the Phase 303 through Phase 318 suffix above, including the final period.
- Runtime `phase_range` becomes `range(168, 319)`.
- Source self-check literal becomes `aggregate_range = "range(168, 319)"`.
- Add split stale aggregate guard for `range(168, 318)`.
- Retain older split stale aggregate guards, including `range(168, 317)` and earlier existing guards.
- Preserve the anchored single `CURRENT_STATUS_PREFIX` assignment guard.
- Preserve the no-discovery-token guards.

## Allowed Files

Executor S1 may edit only:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

Parent controller may materialize/finalize only:
- `design/codestable/features/2026-06-22-hermes-tavern-phase318-attention-status-sync-through-phase317/design.md`
- `design/codestable/features/2026-06-22-hermes-tavern-phase318-attention-status-sync-through-phase317/checklist.yaml`
- `design/codestable/features/2026-06-22-hermes-tavern-phase318-attention-status-sync-through-phase317/acceptance.md`

## Prohibited Files and Actions

Prohibited: runtime/source/plugin/provider/gateway/CLI files, `plugins/`, provider files, `gateway/`, `run_agent.py`, `cli.py`, `gateway/run.py`, plugin runtime files, credentials, root design, README, architecture, roadmap, requirements, compound docs, assets/fixtures/schemas, dependency/config/build files, service lifecycle commands, edits to existing prior phase feature directories, broad rewrites, executor staging, commit, push, messages, and progress-state updates.

## Implementation Steps

S1: Sync status artifacts.
- Update only `attention.md` prefix and append only the Phase 318 label.
- Update only focused test constants, required label list, suffix, phase range, aggregate range, stale markers, stale split aggregate guards, and existing no-discovery-token guards.
- Do not finalize checklist or acceptance.

S2: Parent verification and finalization.
- Parent controller runs required validation commands.
- Confirm changed and untracked paths are limited to allowed files.
- Finalize checklist/acceptance only after verification.
- If any gate fails, leave status non-final and report the failing command.

## Stale-Marker Guards

- `attention.md` must not contain stale terminal status `All phases 1-317 accepted` after the update.
- `attention.md` must not contain standalone stale markers `1-317` or `1–317`.
- Test source may contain stale values only as intentional `STALE_*` constants/assertions or split stale aggregate guards.
- Add split stale aggregate guard for `range(168, 318)` and retain older split guards.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-22-hermes-tavern-phase318-attention-status-sync-through-phase317 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts='`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- Static guard for stale standalone `1-317` patterns in `attention.md` and intentional-only stale values in `tests/test_hermes_tavern_codestable_status.py`.
- Static allowlist guard for changed/untracked paths.
- `git diff --check`
- `git diff --cached --check`

## Risks and Rollback

Risks:
- Duplicate final `and` placement in the long attention suffix.
- Leaving stale `1-317` markers in the attention current-status bullet.
- Creating duplicate or stale `CURRENT_STATUS_PREFIX` assignments in the focused test.
- Touching runtime/plugin/provider/gateway/source/dependency/config paths outside this status-only slice.

Rollback point: revert only the Phase 318 allowed files to the pre-executor state; because executor must not stage, commit, push, finalize acceptance, or update progress state, rollback is limited to the dirty working tree before parent closeout.

## Executor Prompt

Implement only Phase 318 attention/status sync through accepted Phase 317. Edit only `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py`. Advance current status to `All phases 1-318 accepted`, preserve `Phase 121-167` and every explicit Phase 168 through Phase 317 label, append exactly `Phase 318 attention status sync through Phase 317`, and do not add any Phase 319 attention/status label. Update focused test constants, suffix, required labels, `range(168, 319)`, `aggregate_range = "range(168, 319)"`, stale markers for `All phases 1-317 accepted`, and split stale aggregate guard for `range(168, 318)` while retaining older stale guards. Preserve no-discovery-token guards and the single `CURRENT_STATUS_PREFIX` assignment guard. Do not commit, push, stage, update state, send messages, touch runtime/protected paths, change dependencies, edit prior phase directories, finalize checklist/acceptance, or run service lifecycle commands.

## Review Criteria

Architect review should output `PASS` only if the current diff matches this artifact, all changed/untracked files are within the allowed list, the current-status prefix/suffix/labels are exact with only one final `and`, the focused status test has exactly one anchored `CURRENT_STATUS_PREFIX` assignment and the required stale/no-discovery guards, verification gates pass or full pytest infeasibility is documented, and acceptance remains parent-pending/non-final until parent verification. Otherwise output `REQUEST_CHANGES` with the first concrete mismatch.
