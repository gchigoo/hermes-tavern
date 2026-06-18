---
doc_type: feature-design
status: approved
feature: "2026-06-18-hermes-tavern-phase303-attention-status-sync-through-phase302"
date: "2026-06-18"
owner: company-boost
implementation_ready: true
parent_verification_required: true
no_commit_or_push_performed: true
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase303]
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 302 only, without changing runtime behavior.
---

# Phase 303: CodeStable Attention Status Sync Through Phase 302

## Gate

Phase 302 is accepted at `design/codestable/features/2026-06-18-hermes-tavern-phase302-attention-status-sync-through-phase301/acceptance.md`.

Current state:
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-301 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` enforces the Phase 301 prefix and `range(168, 302)`.
- No Phase 303 status-sync feature directory existed before this controller materialization.

## Goals

- Advance exactly one recurring status-sync phase: Phase 303 syncs through accepted Phase 302 only.
- Update only `attention.md`, the focused static status test, and this Phase 303 design/checklist.
- Leave the dirty tree uncommitted for parent-controller verification.
- Keep acceptance absent/pending until controller verification.

## Non-Goals

- Do not touch runtime/source/plugin/provider/gateway/CLI/root-design/README/architecture/roadmap/requirements/compound/build/asset/fixture files.
- Do not change dependencies, service lifecycle behavior, model/provider routing, credentials, adult-fiction/RP compatibility, or provider safety behavior.
- Do not create, draft, or finalize `acceptance.md` in executor scope.
- Do not stage, commit, push, update progress state, or perform broad rewrites.

This lane is docs/static-test/status-only. Adult-fiction/RP compatibility and provider safety boundaries are unaffected and must remain untouched.

## Exact Status Contract

Change the `attention.md` current-status prefix:
- From: `Current status (2026-06-18): All phases 1-301 accepted`
- To: `Current status (2026-06-18): All phases 1-302 accepted`

Append exactly once:
- `Phase 302 attention status sync through Phase 301`

Preserve:
- `Phase 121-167`
- Every explicit `Phase 168` through `Phase 301` short label exactly as already written.

Do not add:
- Any `Phase 303` attention/status label to `attention.md`.

Final suffix must become exactly:
`Phase 300 attention status sync through Phase 299, Phase 301 attention status sync through Phase 300, and Phase 302 attention status sync through Phase 301.`

## Focused Test Contract

Update `tests/test_hermes_tavern_codestable_status.py`:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-302 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-301 accepted"`
- `STALE_PHASE_MARKER = "1-301"`
- `STALE_PHASE_MARKER_EN_DASH = "1–301"`
- Append `Phase 302 attention status sync through Phase 301` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing required label through Phase 301.
- `FINAL_STATUS_SUFFIX` equals the Phase 300/301/302 suffix above.
- Runtime `phase_range` becomes `range(168, 303)`.
- Source self-check literal becomes `aggregate_range = "range(168, 303)"`.
- Add split stale aggregate guard for `range(168, 302)`.
- Retain older split stale guards including 301, 300, 299, 298, 297, and earlier existing guards.
- Preserve anchored `CURRENT_STATUS_PREFIX` assignment-count regex.
- Preserve split discovery-token guards for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk`.

## Allowed Files

Executor may edit only:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-18-hermes-tavern-phase303-attention-status-sync-through-phase302/design.md`
- `design/codestable/features/2026-06-18-hermes-tavern-phase303-attention-status-sync-through-phase302/checklist.yaml`

## Prohibited Files and Actions

Prohibited: runtime/source/plugin/provider/gateway/CLI/root-design/README/architecture/roadmap/requirements/compound/build/asset/fixture files, service lifecycle commands, dependency changes, broad rewrites, acceptance finalization or creation, staging, commit, and push.

## Implementation Steps

S1: Sync status artifacts.
- Update `attention.md` prefix and append only the Phase 302 label.
- Update focused test constants, required label list, suffix, phase range, aggregate range, stale markers, stale split aggregate guards, and discovery-token guards.

S2: Verify and hand off.
- Run required validation commands.
- Confirm changed/untracked paths are limited to allowed files.
- Leave acceptance absent/pending for controller verification.

## Stale-Marker Guards

- `attention.md` must not contain stale terminal status `All phases 1-301 accepted` after the update.
- `attention.md` must not contain standalone stale markers `1-301` or `1–301`.
- Test source may contain stale values only as intentional `STALE_*` constants/assertions or split stale aggregate guards.
- Add split stale aggregate guard for `range(168, 302)` and retain older split guards.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-18-hermes-tavern-phase303-attention-status-sync-through-phase302 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts='`
- Python static status/protected-path guard over allowed paths, exact prefix/suffix/labels/ranges, stale markers, anchored assignment regex, and split discovery-token guards.
- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='`

## Executor Prompt

Implement only Phase 303 attention/status sync through accepted Phase 302. Edit only `design/codestable/attention.md`, `tests/test_hermes_tavern_codestable_status.py`, and the Phase 303 `design.md`/`checklist.yaml`. Advance current status to `All phases 1-302 accepted`, preserve `Phase 121-167` and every explicit Phase 168 through Phase 301 label, append exactly `Phase 302 attention status sync through Phase 301`, and do not add any Phase 303 attention/status label. Update focused test constants, suffix, required labels, `range(168, 303)`, `aggregate_range = "range(168, 303)"`, stale markers, and split stale aggregate guard for `range(168, 302)`. Keep `acceptance.md` absent/pending until controller verification. Do not commit, push, stage, update state, touch runtime/protected paths, change dependencies, or run service lifecycle commands.
