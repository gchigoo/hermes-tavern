---
doc_type: feature-design
status: approved
feature: "2026-06-22-hermes-tavern-phase311-attention-status-sync-through-phase310"
date: "2026-06-22"
owner: standard-lane
implementation_ready: true
parent_verification_required: true
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase311]
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 310 only, without changing runtime behavior.
---

# Phase 311: CodeStable Attention Status Sync Through Phase 310

## Gate

Phase 310 is accepted at `design/codestable/features/2026-06-22-hermes-tavern-phase310-attention-status-sync-through-phase309/acceptance.md`.

Current state before this slice:
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-310 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` enforces the Phase 310 prefix and `range(168, 311)`.
- No Phase 311 status-sync feature directory existed before this controller materialization.

## Goals

- Advance exactly one recurring status-sync phase: Phase 311 syncs through accepted Phase 310 only.
- Update only `attention.md`, the focused static status test, and this Phase 311 feature artifact directory.
- Preserve Hermes-native plugin architecture and SillyTavern asset compatibility by avoiding all runtime and asset changes.
- Keep adult-fiction/RP compatibility unchanged and do not introduce or weaken any safety boundary involving minors or provider safety systems.
- Leave the dirty tree uncommitted for parent-controller authoritative verification, commit, push, CI watch, and progress-state update.

## Non-Goals

- Do not touch runtime/source/plugin/provider/gateway/CLI/root-design/README/architecture/roadmap/requirements/compound/build/asset/fixture files.
- Do not change dependencies, service lifecycle behavior, model/provider routing, credentials, adult-fiction/RP compatibility, provider safety behavior, network behavior, or configuration files.
- Do not add a Phase 311 attention/status label; this slice records Phase 310 as the newly accepted completed phase.
- Do not edit existing prior phase feature directories.
- Do not let the worker/executor stage, commit, push, force-push, send messages, update progress state, or perform broad rewrites; parent controller owns final closeout.

This lane is docs/static-test/status-only. Hermes-native plugin architecture, SillyTavern asset compatibility, and provider/runtime behavior are unaffected and must remain untouched.

## Exact Status Contract

Change the `attention.md` current-status prefix:
- From: `Current status (2026-06-18): All phases 1-310 accepted`
- To: `Current status (2026-06-18): All phases 1-311 accepted`

Append exactly once after `Phase 310 attention status sync through Phase 309`:
- `Phase 311 attention status sync through Phase 310`

Preserve:
- `Phase 121-167`
- Every explicit `Phase 168` through `Phase 310` short label exactly as already written.

Do not add:
- Any `Phase 312` attention/status label to `attention.md` or the focused status label list.

Final suffix must become exactly:
`Phase 303 attention status sync through Phase 302, Phase 304 attention status sync through Phase 303, Phase 305 attention status sync through Phase 304, Phase 306 attention status sync through Phase 305, Phase 307 attention status sync through Phase 306, Phase 308 attention status sync through Phase 307, Phase 309 attention status sync through Phase 308, Phase 310 attention status sync through Phase 309, and Phase 311 attention status sync through Phase 310.`

## Focused Test Contract

Update `tests/test_hermes_tavern_codestable_status.py`:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-311 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-310 accepted"`
- `STALE_PHASE_MARKER = "1-310"`
- `STALE_PHASE_MARKER_EN_DASH = "1–310"`
- Append `Phase 311 attention status sync through Phase 310` to `REQUIRED_PHASE_LABELS` exactly once.
- Preserve every existing required label through Phase 310.
- `FINAL_STATUS_SUFFIX` equals the Phase 303/304/305/306/307/308/309/310/311 suffix above.
- Runtime `phase_range` becomes `range(168, 312)`.
- Source self-check literal becomes `aggregate_range = "range(168, 312)"`.
- Add split stale aggregate guard for `range(168, 311)`.
- Retain older split stale guards including 310, 309, 308, 307, 306, 305, 304, 303, 302, 301, 300, 299, 298, 297, 296, and earlier existing guards.
- Preserve anchored `CURRENT_STATUS_PREFIX` assignment-count regex.
- Preserve split discovery-token guards for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk` without embedding those discovery calls contiguously except via split strings.

## Allowed Files

Executor may edit only:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-22-hermes-tavern-phase311-attention-status-sync-through-phase310/design.md`
- `design/codestable/features/2026-06-22-hermes-tavern-phase311-attention-status-sync-through-phase310/checklist.yaml`
- `design/codestable/features/2026-06-22-hermes-tavern-phase311-attention-status-sync-through-phase310/acceptance.md` only as parent-pending/non-final evidence if created before parent verification.

## Prohibited Files and Actions

Prohibited: runtime/source/plugin/provider/gateway/CLI files, `plugins/`, provider files, `gateway/`, `run_agent.py`, `cli.py`, `gateway/run.py`, plugin runtime files, credentials, root design, README, architecture, roadmap, requirements, compound docs, build outputs, assets/fixtures/schemas, service lifecycle commands, dependency changes, broad rewrites, edits to existing prior phase feature directories, staging, commit, push, force-push, messages, and progress-state updates.

## Implementation Steps

S1: Sync status artifacts.
- Update `attention.md` prefix and append only the Phase 311 label.
- Update focused test constants, required label list, suffix, phase range, aggregate range, stale markers, stale split aggregate guards, and discovery-token guards.

S2: Verify and prepare parent handoff.
- Run required validation commands.
- Confirm changed and untracked paths are limited to allowed files.
- If worker verification gates pass, record evidence in checklist/acceptance while keeping status parent-pending/non-final and `parent_verification_required: true`.
- If any gate fails, leave status non-final and report the failing command.

## Stale-Marker Guards

- `attention.md` must not contain stale terminal status `All phases 1-310 accepted` after the update.
- `attention.md` must not contain standalone stale markers `1-310` or `1–310`.
- Test source may contain stale values only as intentional `STALE_*` constants/assertions or split stale aggregate guards.
- Add split stale aggregate guard for `range(168, 311)` and retain older split guards.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-22-hermes-tavern-phase311-attention-status-sync-through-phase310 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts='`
- Python static status/protected-path guard over allowed paths, exact prefix/suffix/labels/ranges, stale markers, anchored assignment regex, and split discovery-token guards.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='`
- `git diff --check`

## Risks and Rollback

Risks:
- Duplicate final `and` placement in the long attention suffix.
- Adding a Phase 311 label instead of only the Phase 310 label in the status line — wait, this design is for syncing THROUGH Phase 310 (meaning Phase 310 acceptance becomes the new status). The attention status advances to `1-311 accepted` and the Phase 311 label is appended.
- Leaving stale `1-310` markers in the attention current-status bullet.
- Creating duplicate or stale `CURRENT_STATUS_PREFIX` assignments in the focused test.
- Touching runtime/plugin/provider/gateway/source/dependency/config paths outside this status-only slice.

Rollback point: revert only the five allowed Phase 311 files to the pre-executor state; because no staging/commit/push occurs in this lane, rollback is limited to the dirty working tree.

## Executor Prompt

Implement only Phase 311 attention/status sync through accepted Phase 310. Edit only `design/codestable/attention.md`, `tests/test_hermes_tavern_codestable_status.py`, and files inside `design/codestable/features/2026-06-22-hermes-tavern-phase311-attention-status-sync-through-phase310/`. Advance current status to `All phases 1-311 accepted`, preserve `Phase 121-167` and every explicit Phase 168 through Phase 310 label, append exactly `Phase 311 attention status sync through Phase 310`, and do not add any Phase 312 attention/status label. Update focused test constants, suffix, required labels, `range(168, 312)`, `aggregate_range = "range(168, 312)"`, stale markers for `All phases 1-310 accepted`, and split stale aggregate guard for `range(168, 311)`. Do not commit, push, stage, update state, send messages, touch runtime/protected paths, change dependencies, edit prior phase directories, or run service lifecycle commands.

## Review Criteria

Architect review should output `PASS` only if the current diff matches this artifact, all changed/untracked files are within the allowed list, the current-status prefix/suffix/labels are exact with only one final `and`, the focused status test has exactly one anchored `CURRENT_STATUS_PREFIX` assignment and the required stale/discovery guards, verification gates pass or full pytest infeasibility is documented, and acceptance remains parent-pending/non-final until parent verification. Otherwise output `REQUEST_CHANGES` with the first concrete mismatch.
