---
doc_type: feature-design
status: approved
feature: "2026-06-22-hermes-tavern-phase314-attention-status-sync-through-phase313"
date: "2026-06-22"
owner: company-boost
implementation_ready: true
parent_verification_required: true
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase314]
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 313 only, without changing runtime behavior.
---

# Phase 314: CodeStable Attention Status Sync Through Phase 313

## Gate

Phase 313 is accepted at `design/codestable/features/2026-06-22-hermes-tavern-phase313-attention-status-sync-through-phase312/acceptance.md`.

Current state before this slice:
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-313 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` enforces the Phase 313 prefix and `range(168, 314)`.
- No Phase 314 status-sync feature directory existed before this controller materialization.

## Goals

- Advance exactly one recurring status-sync phase: Phase 314 syncs through accepted Phase 313 only.
- Update only `attention.md`, the focused static status test, and this Phase 314 feature artifact directory.
- Preserve Hermes-native plugin architecture and SillyTavern asset compatibility by avoiding all runtime and asset changes.
- Keep adult-fiction/RP compatibility unchanged and do not introduce or weaken any safety boundary involving minors or provider safety systems.
- Leave the dirty tree uncommitted for parent-controller authoritative verification, commit, push, CI watch, and progress-state update.

## Non-Goals

- Do not touch runtime/source/plugin/provider/gateway/CLI/root-design/README/architecture/roadmap/requirements/compound/build/asset/fixture files.
- Do not change dependencies, service lifecycle behavior, model/provider routing, credentials, adult-fiction/RP compatibility, provider safety behavior, network behavior, or configuration files.
- Do not add a Phase 315 attention/status label; this slice records Phase 314 as the newly accepted completed phase.
- Do not edit existing prior phase feature directories.
- Do not let the worker/executor stage, commit, push, force-push, send messages, update progress state, or perform broad rewrites; parent controller owns final closeout.

This lane is docs/static-test/status-only. Hermes-native plugin architecture, SillyTavern asset compatibility, and provider/runtime behavior are unaffected and must remain untouched.

## Exact Status Contract

Change the `attention.md` current-status prefix:
- From: `Current status (2026-06-18): All phases 1-313 accepted`
- To: `Current status (2026-06-18): All phases 1-314 accepted`

Append exactly once after `Phase 313 attention status sync through Phase 312`:
- Convert `and Phase 313 attention status sync through Phase 312.`
- To `Phase 313 attention status sync through Phase 312, and Phase 314 attention status sync through Phase 313.`

Preserve:
- `Phase 121-167`
- Every explicit `Phase 168` through `Phase 313` short label exactly as already written.

Do not add:
- Any `Phase 315` attention/status label to `attention.md` or the focused status label list.

Final suffix must become exactly:
`Phase 303 attention status sync through Phase 302, Phase 304 attention status sync through Phase 303, Phase 305 attention status sync through Phase 304, Phase 306 attention status sync through Phase 305, Phase 307 attention status sync through Phase 306, Phase 308 attention status sync through Phase 307, Phase 309 attention status sync through Phase 308, Phase 310 attention status sync through Phase 309, Phase 311 attention status sync through Phase 310, Phase 312 attention status sync through Phase 311, Phase 313 attention status sync through Phase 312, and Phase 314 attention status sync through Phase 313.`

## Focused Test Contract

Update `tests/test_hermes_tavern_codestable_status.py`:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-314 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-313 accepted"`
- `STALE_PHASE_MARKER = "1-313"`
- `STALE_PHASE_MARKER_EN_DASH = "1–313"`
- Append `Phase 314 attention status sync through Phase 313` to `REQUIRED_PHASE_LABELS` exactly once.
- Preserve every existing required label through Phase 313.
- `FINAL_STATUS_SUFFIX` equals the Phase 303/304/305/306/307/308/309/310/311/312/313/314 suffix above.
- Runtime `phase_range` becomes `range(168, 315)`.
- Source self-check literal becomes `aggregate_range = "range(168, 315)"`.
- Add split stale aggregate guard for `range(168, 314)`.
- Retain older split stale guards including 313, 312, 311, 310, 309, 308, 307, 306, 305, 304, 303, 302, 301, 300, 299, 298, 297, 296, and earlier existing guards.
- Preserve anchored `CURRENT_STATUS_PREFIX` assignment-count regex.
- Preserve split discovery-token guards for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk` without embedding those discovery calls contiguously except via split strings.

## Allowed Files

Executor may edit only:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-22-hermes-tavern-phase314-attention-status-sync-through-phase313/design.md`
- `design/codestable/features/2026-06-22-hermes-tavern-phase314-attention-status-sync-through-phase313/checklist.yaml`
- `design/codestable/features/2026-06-22-hermes-tavern-phase314-attention-status-sync-through-phase313/acceptance.md` only as parent-pending/non-final evidence if created before parent verification.

## Prohibited Files and Actions

Prohibited: runtime/source/plugin/provider/gateway/CLI files, `plugins/`, provider files, `gateway/`, `run_agent.py`, `cli.py`, `gateway/run.py`, plugin runtime files, credentials, root design, README, architecture, roadmap, requirements, compound docs, build outputs, assets/fixtures/schemas, service lifecycle commands, dependency changes, broad rewrites, edits to existing prior phase feature directories, staging, commit, push, force-push, messages, and progress-state updates.

## Implementation Steps

S1: Sync status artifacts.
- Update `attention.md` prefix and append only the Phase 314 label.
- Update focused test constants, required label list, suffix, phase range, aggregate range, stale markers, stale split aggregate guards, and discovery-token guards.

S2: Verify and prepare parent handoff.
- Run required validation commands.
- Confirm changed and untracked paths are limited to allowed files.
- If worker verification gates pass, record evidence in checklist/acceptance while keeping status parent-pending/non-final and `parent_verification_required: true`.
- If any gate fails, leave status non-final and report the failing command.

## Stale-Marker Guards

- `attention.md` must not contain stale terminal status `All phases 1-313 accepted` after the update.
- `attention.md` must not contain standalone stale markers `1-313` or `1–313`.
- Test source may contain stale values only as intentional `STALE_*` constants/assertions or split stale aggregate guards.
- Add split stale aggregate guard for `range(168, 314)` and retain older split guards.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-22-hermes-tavern-phase314-attention-status-sync-through-phase313 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts='`
- Python static status/protected-path guard over allowed paths, exact prefix/suffix/labels/ranges, stale markers, anchored assignment regex, and split discovery-token guards.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='`
- `git diff --check`

## Risks and Rollback

Risks:
- Duplicate final `and` placement in the long attention suffix.
- Leaving stale `1-313` markers in the attention current-status bullet.
- Creating duplicate or stale `CURRENT_STATUS_PREFIX` assignments in the focused test.
- Touching runtime/plugin/provider/gateway/source/dependency/config paths outside this status-only slice.

Rollback point: revert only the five allowed Phase 314 files to the pre-executor state; because no staging/commit/push occurs in this lane, rollback is limited to the dirty working tree.

## Executor Prompt

Implement only Phase 314 attention/status sync through accepted Phase 313. Edit only `design/codestable/attention.md`, `tests/test_hermes_tavern_codestable_status.py`, and files inside `design/codestable/features/2026-06-22-hermes-tavern-phase314-attention-status-sync-through-phase313/`. Advance current status to `All phases 1-314 accepted`, preserve `Phase 121-167` and every explicit Phase 168 through Phase 313 label, append exactly `Phase 314 attention status sync through Phase 313`, and do not add any Phase 315 attention/status label. Update focused test constants, suffix, required labels, `range(168, 315)`, `aggregate_range = "range(168, 315)"`, stale markers for `All phases 1-313 accepted`, and split stale aggregate guard for `range(168, 314)`. Do not commit, push, stage, update state, send messages, touch runtime/protected paths, change dependencies, edit prior phase directories, or run service lifecycle commands.

## Review Criteria

Architect review should output `PASS` only if the current diff matches this artifact, all changed/untracked files are within the allowed list, the current-status prefix/suffix/labels are exact with only one final "and", the focused status test has exactly one anchored `CURRENT_STATUS_PREFIX` assignment and the required stale/discovery guards, verification gates pass or full pytest infeasibility is documented, and acceptance remains parent-pending/non-final until parent verification. Otherwise output `REQUEST_CHANGES` with the first concrete mismatch.
