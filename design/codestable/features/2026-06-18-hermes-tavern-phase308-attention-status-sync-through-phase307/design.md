---
doc_type: feature-design
status: approved
feature: "2026-06-18-hermes-tavern-phase308-attention-status-sync-through-phase307"
date: "2026-06-18"
owner: company-boost
implementation_ready: true
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase308]
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 307 only, without changing runtime behavior.
---

# Phase 308: CodeStable Attention Status Sync Through Phase 307

## Gate

Phase 307 is accepted at `design/codestable/features/2026-06-18-hermes-tavern-phase307-attention-status-sync-through-phase306/acceptance.md`.

Current state before this slice:
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-306 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` enforces the Phase 306 prefix and `range(168, 307)`.
- No Phase 308 status-sync feature directory existed before this controller materialization.

## Goals

- Advance exactly one recurring status-sync phase: Phase 308 syncs through accepted Phase 307 only.
- Update only `attention.md`, the focused static status test, and this Phase 308 feature artifact directory.
- Preserve Hermes-native plugin architecture and SillyTavern asset compatibility by avoiding all runtime and asset changes.
- Parent controller performs final verification, commit, push, CI watch, and progress-state update after this bounded lane passes.

## Non-Goals

- Do not touch runtime/source/plugin/provider/gateway/CLI/root-design/README/architecture/roadmap/requirements/compound/build/asset/fixture files.
- Do not change dependencies, service lifecycle behavior, model/provider routing, credentials, adult-fiction/RP compatibility, or provider safety behavior.
- Do not edit existing prior phase feature directories.
- Do not let the worker/executor stage, commit, push, update progress state, or perform broad rewrites; parent controller owns final closeout.

This lane is docs/static-test/status-only. Adult-fiction/RP compatibility and provider safety boundaries are unaffected and must remain untouched.

## Exact Status Contract

Change the `attention.md` current-status prefix:
- From: `Current status (2026-06-18): All phases 1-306 accepted`
- To: `Current status (2026-06-18): All phases 1-307 accepted`

Append exactly once (after "Phase 306 attention status sync through Phase 305"):
- `Phase 307 attention status sync through Phase 306`

Preserve:
- `Phase 121-167`
- Every explicit `Phase 168` through `Phase 306` short label exactly as already written.

Do not add:
- Any `Phase 308` attention/status label to `attention.md`.

Final suffix must become exactly:
`Phase 302 attention status sync through Phase 301, Phase 303 attention status sync through Phase 302, Phase 304 attention status sync through Phase 303, Phase 305 attention status sync through Phase 304, Phase 306 attention status sync through Phase 305, and Phase 307 attention status sync through Phase 306.`

## Focused Test Contract

Update `tests/test_hermes_tavern_codestable_status.py`:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-307 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-306 accepted"`
- `STALE_PHASE_MARKER = "1-306"`
- `STALE_PHASE_MARKER_EN_DASH = "1–306"`
- Append `Phase 307 attention status sync through Phase 306` to `REQUIRED_PHASE_LABELS` exactly once.
- Preserve every existing required label through Phase 306.
- `FINAL_STATUS_SUFFIX` equals the Phase 302/303/304/305/306/307 suffix above.
- Runtime `phase_range` becomes `range(168, 308)`.
- Source self-check literal becomes `aggregate_range = "range(168, 308)"`.
- Add split stale aggregate guard for `range(168, 307)`.
- Retain older split stale guards including 306, 305, 304, 303, 302, 301, 300, 299, 298, 297, and earlier existing guards.
- Preserve anchored `CURRENT_STATUS_PREFIX` assignment-count regex.
- Preserve split discovery-token guards for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk` without embedding those discovery calls contiguously except via split strings.

## Allowed Files

Executor may edit only:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-18-hermes-tavern-phase308-attention-status-sync-through-phase307/design.md`
- `design/codestable/features/2026-06-18-hermes-tavern-phase308-attention-status-sync-through-phase307/checklist.yaml`
- `design/codestable/features/2026-06-18-hermes-tavern-phase308-attention-status-sync-through-phase307/acceptance.md` only after real worker-controller verification gates pass.

## Prohibited Files and Actions

Prohibited: runtime/source/plugin/provider/gateway/CLI files, `plugins/`, provider files, `gateway/`, `run_agent.py`, `cli.py`, `gateway/run.py`, plugin runtime files, credentials, root design, README, architecture, roadmap, requirements, compound docs, build outputs, assets/fixtures/schemas, service lifecycle commands, dependency changes, broad rewrites, edits to existing prior phase feature directories, staging, commit, push, and progress-state updates.

## Implementation Steps

S1: Sync status artifacts.
- Update `attention.md` prefix and append only the Phase 307 label.
- Update focused test constants, required label list, suffix, phase range, aggregate range, stale markers, stale split aggregate guards, and discovery-token guards.

S2: Verify and finalize the feature artifacts.
- Run required validation commands.
- Confirm changed and untracked paths are limited to allowed files.
- If all worker verification gates pass, set checklist and acceptance evidence to accepted based on those real command results while keeping parent verification required before commit/push.
- If any gate fails, leave status non-final and report the failing command.

## Stale-Marker Guards

- `attention.md` must not contain stale terminal status `All phases 1-306 accepted` after the update.
- `attention.md` must not contain standalone stale markers `1-306` or `1–306`.
- Test source may contain stale values only as intentional `STALE_*` constants/assertions or split stale aggregate guards.
- Add split stale aggregate guard for `range(168, 307)` and retain older split guards.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-18-hermes-tavern-phase308-attention-status-sync-through-phase307 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts='`
- Python static status/protected-path guard over allowed paths, exact prefix/suffix/labels/ranges, stale markers, anchored assignment regex, and split discovery-token guards.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='`
- `git diff --check`

## Executor Prompt

Implement only Phase 308 attention/status sync through accepted Phase 307. Edit only `design/codestable/attention.md`, `tests/test_hermes_tavern_codestable_status.py`, and files inside the Phase 308 feature directory. Advance current status to `All phases 1-307 accepted`, preserve `Phase 121-167` and every explicit Phase 168 through Phase 306 label, append exactly `Phase 307 attention status sync through Phase 306`, and do not add any Phase 308 attention/status label. Update focused test constants, suffix, required labels, `range(168, 308)`, `aggregate_range = "range(168, 308)"`, stale markers for `All phases 1-306 accepted`, and split stale aggregate guard for `range(168, 307)`. Do not commit, push, stage, update state, touch runtime/protected paths, change dependencies, edit prior phase directories, or run service lifecycle commands.
