---
doc_type: feature-design
status: approved
feature: "2026-06-18-hermes-tavern-phase304-attention-status-sync-through-phase303"
date: "2026-06-18"
owner: company-boost
implementation_ready: true
parent_verification_required: true
no_commit_or_push_performed: true
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase304]
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 303 only, without changing runtime behavior.
---

# Phase 304: CodeStable Attention Status Sync Through Phase 303

## Gate

Phase 303 is accepted at `design/codestable/features/2026-06-18-hermes-tavern-phase303-attention-status-sync-through-phase302/acceptance.md`.

Current state:
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-302 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` enforces the Phase 302 prefix and `range(168, 303)`.
- No Phase 304 status-sync feature directory existed before this controller materialization.

## Goals

- Advance exactly one recurring status-sync phase: Phase 304 syncs through accepted Phase 303 only.
- Update only `attention.md`, the focused static status test, and this Phase 304 design/checklist.
- Leave the dirty tree uncommitted for parent-controller verification.
- Keep `acceptance.md` absent unless parent-controller closeout explicitly finalizes it later.

## Non-Goals

- Do not touch runtime/source/plugin/provider/gateway/CLI/root-design/README/architecture/roadmap/requirements/compound/build/asset/fixture files.
- Do not change dependencies, service lifecycle behavior, model/provider routing, credentials, adult-fiction/RP compatibility, or provider safety behavior.
- Do not create, draft, or finalize `acceptance.md` in executor scope.
- Do not stage, commit, push, update progress state, or perform broad rewrites.

This lane is docs/static-test/status-only. Adult-fiction/RP compatibility and provider safety boundaries are unaffected and must remain untouched.

## Exact Status Contract

Change the `attention.md` current-status prefix:
- From: `Current status (2026-06-18): All phases 1-302 accepted`
- To: `Current status (2026-06-18): All phases 1-303 accepted`

Append exactly once:
- `Phase 303 attention status sync through Phase 302`

Preserve:
- `Phase 121-167`
- Every explicit `Phase 168` through `Phase 302` short label exactly as already written.

Do not add:
- Any `Phase 304` attention/status label to `attention.md`.

Final suffix must become exactly:
`Phase 301 attention status sync through Phase 300, Phase 302 attention status sync through Phase 301, and Phase 303 attention status sync through Phase 302.`

## Focused Test Contract

Update `tests/test_hermes_tavern_codestable_status.py`:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-303 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-302 accepted"`
- `STALE_PHASE_MARKER = "1-302"`
- `STALE_PHASE_MARKER_EN_DASH = "1–302"`
- Append `Phase 303 attention status sync through Phase 302` to `REQUIRED_PHASE_LABELS` exactly once.
- Preserve every existing required label through Phase 302.
- `FINAL_STATUS_SUFFIX` equals the Phase 301/302/303 suffix above.
- Runtime `phase_range` becomes `range(168, 304)`.
- Source self-check literal becomes `aggregate_range = "range(168, 304)"`.
- Add split stale aggregate guard for `range(168, 303)`.
- Retain older split stale guards including 302, 301, 300, 299, 298, 297, and earlier existing guards.
- Preserve anchored `CURRENT_STATUS_PREFIX` assignment-count regex.
- Preserve split discovery-token guards for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk` without embedding those discovery calls contiguously except via split strings.

## Allowed Files

Executor may edit only:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-18-hermes-tavern-phase304-attention-status-sync-through-phase303/design.md`
- `design/codestable/features/2026-06-18-hermes-tavern-phase304-attention-status-sync-through-phase303/checklist.yaml`

## Prohibited Files and Actions

Prohibited: runtime/source/plugin/provider/gateway/CLI/root-design/README/architecture/roadmap/requirements/compound/build/asset/fixture files, service lifecycle commands, dependency changes, broad rewrites, acceptance finalization or creation, staging, commit, push, and progress-state updates.

## Implementation Steps

S1: Sync status artifacts.
- Update `attention.md` prefix and append only the Phase 303 label.
- Update focused test constants, required label list, suffix, phase range, aggregate range, stale markers, stale split aggregate guards, and discovery-token guards.

S2: Verify and hand off.
- Run required validation commands.
- Confirm changed/untracked paths are limited to allowed files.
- Leave acceptance absent/pending for parent-controller verification and closeout.

## Stale-Marker Guards

- `attention.md` must not contain stale terminal status `All phases 1-302 accepted` after the update.
- `attention.md` must not contain standalone stale markers `1-302` or `1–302`.
- Test source may contain stale values only as intentional `STALE_*` constants/assertions or split stale aggregate guards.
- Add split stale aggregate guard for `range(168, 303)` and retain older split guards.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-18-hermes-tavern-phase304-attention-status-sync-through-phase303 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts='`
- Python static status/protected-path guard over allowed paths, exact prefix/suffix/labels/ranges, stale markers, anchored assignment regex, and split discovery-token guards.
- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='`

## Executor Prompt

Implement only Phase 304 attention/status sync through accepted Phase 303. Edit only `design/codestable/attention.md`, `tests/test_hermes_tavern_codestable_status.py`, and the Phase 304 `design.md`/`checklist.yaml`. Advance current status to `All phases 1-303 accepted`, preserve `Phase 121-167` and every explicit Phase 168 through Phase 302 label, append exactly `Phase 303 attention status sync through Phase 302`, and do not add any Phase 304 attention/status label. Update focused test constants, suffix, required labels, `range(168, 304)`, `aggregate_range = "range(168, 304)"`, stale markers, and split stale aggregate guard for `range(168, 303)`. Keep `acceptance.md` absent/pending until parent-controller verification. Do not commit, push, stage, update state, touch runtime/protected paths, change dependencies, or run service lifecycle commands.
