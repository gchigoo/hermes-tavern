---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase369-attention-status-sync-through-phase368
title: "Phase 369 attention/status sync through Phase 368"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 369 attention/status sync through accepted Phase 368."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase369, company-boost, parent-handoff]
---

# Phase 369 attention/status sync through Phase 368

## Background / Current State

Phase 368 is accepted at the bounded company-boost baseline.

Inspected baseline:

- Pre-run HEAD: `52873c8` on `main`.
- `design/codestable/features/2026-06-26-hermes-tavern-phase368-attention-status-sync-through-phase367/acceptance.md` exists.
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-368 accepted`.
- The current attention suffix ends with `Phase 366 attention status sync through Phase 365, Phase 367 attention status sync through Phase 366, and Phase 368 attention status sync through Phase 367.`
- `tests/test_hermes_tavern_codestable_status.py` currently pins `CURRENT_STATUS_PREFIX` to Phase 368.
- The focused status test currently uses `phase_range = range(168, 369)` and live aggregate string `range(168, 369)`.
- The focused status test already includes split stale aggregate guard `stale_aggregate_range_368`.
- The Phase 369 feature directory is absent before S1.

Range note: Phase 369 must advance the live range to `range(168, 370)` and add a split stale guard for stale `range(168, 369)`.

## Goals

- Materialize the Phase 369 design/checklist artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-368 to 1-369.
- Append `Phase 369 attention status sync through Phase 368` exactly once to the current status line.
- Update the focused status regression to guard the Phase 369 live status contract.
- Preserve `Phase 121-167 novel project layer + metadata + JSON export for all entity types`.
- Preserve every explicit Phase 168 through Phase 368 label, especially `Phase 368 attention status sync through Phase 367`.
- Leave the checklist in non-final S1 handoff state for parent verification.

## Non-Goals

- No `acceptance.md` creation during executor S1.
- No Phase 370 work.
- No runtime/source/plugin/provider/gateway/CLI/config/network/dependency/build/cache/service lifecycle changes.
- No root docs, README, architecture, roadmap, requirements, or compound edits.
- No `run_agent.py`, `cli.py`, or `gateway/run.py` edits.
- No broad rewrites, package installs, service starts, staging, commits, pushes, resets, or branch changes.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No provider safety/content behavior changes.
- No adult-fiction/RP behavior changes; no minors-related behavior changes.

## Allowed / Prohibited Scope

Executor S1 may edit only exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase369-attention-status-sync-through-phase368/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase369-attention-status-sync-through-phase368/checklist.yaml`

Creating the Phase 369 feature directory solely to hold `design.md` and `checklist.yaml` is allowed. Creating `acceptance.md` is prohibited.

Checklist state after executor S1 must remain non-final:

- `status: implemented`
- `workflow_status: pending_parent_verification`
- `acceptance_state: pending_parent_verification`
- `parent_verification_required: true`
- `worker_commit_or_push_performed: false`
- `acceptance_artifact: null`

S1 checks may be marked `completed` after the executor finishes. S2 parent verification checks must remain `pending`.

## Exact Mechanical Changes

### attention.md

- Change `All phases 1-368 accepted` to `All phases 1-369 accepted`.
- Append `Phase 369 attention status sync through Phase 368` exactly once.
- Move the terminal `and` from Phase 368 to Phase 369.
- Final attention/test suffix after S1 must be exactly: `Phase 367 attention status sync through Phase 366, Phase 368 attention status sync through Phase 367, and Phase 369 attention status sync through Phase 368.`

### tests/test_hermes_tavern_codestable_status.py

Set constants exactly:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-369 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-368 accepted"`
- `STALE_PHASE_MARKER = "1-368"`
- `STALE_PHASE_MARKER_EN_DASH = "1–368"`
- `FINAL_STATUS_SUFFIX = "Phase 367 attention status sync through Phase 366, Phase 368 attention status sync through Phase 367, and Phase 369 attention status sync through Phase 368."`

Required label list:

- Append `"Phase 369 attention status sync through Phase 368"` to `REQUIRED_PHASE_LABELS` exactly once.
- Preserve every prior label, including all explicit Phase 168 through Phase 368 labels.

Range and stale aggregate updates:

- Set `phase_range = range(168, 370)`.
- Use live aggregate string `"range(168, 370)"` wherever the test asserts the live aggregate.
- Add `stale_aggregate_range_369 = "".join(["range(168, ", "36", "9", ")"])`.
- Include `stale_aggregate_range_369` in the stale assertion tuple.
- Ensure direct stale range literal `range(168, 369)` is absent from test source after S1 except via split-string guard components.
- Existing split guard variables for prior phases may remain.

Guard preservation:

- Keep no-discovery-token guards for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk`.
- Keep single anchored assignment guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; count with anchored regex, not naive substring counts.

## Stale Guard Pitfalls

- Do not remove or rename `Phase 368 attention status sync through Phase 367`.
- Do not leave `range(168, 369)` as a contiguous literal in the test source after S1.
- Do not update only one `aggregate_range` assertion if more than one live aggregate assertion remains.
- Do not count `CURRENT_STATUS_PREFIX` or `FINAL_STATUS_SUFFIX` with naive substring checks; preserve the anchored regex assignment guards.
- Do not create Phase 369 `acceptance.md`; absence is part of the S1 contract.

## Structure Health / Microrefactor

No microrefactor. This slice is docs/static-test status synchronization only. It must not alter runtime files, plugin layout, provider routing, gateway behavior, architecture documents, or dependency/configuration surfaces.

## Verification Commands

Run from repository root:

- `export HERMES_HOME=/Users/steven/.hermes`
- `unset HERMES_SESSION_KEY HERMES_SESSION_ID`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-26-hermes-tavern-phase369-attention-status-sync-through-phase368/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-26-hermes-tavern-phase369-attention-status-sync-through-phase368/checklist.yaml --yaml-only`
- cache-free py_compile for `tests/test_hermes_tavern_codestable_status.py`
- focused pytest with plugin autoload disabled and addopts cleared
- static status/scope guard asserting the exact Phase 369 contract, allowlist, no staged files, no acceptance artifact, no stale direct range literal, and non-final checklist state
- `test ! -e design/codestable/features/2026-06-26-hermes-tavern-phase369-attention-status-sync-through-phase368/acceptance.md`
- `git diff --check`
- `git diff --cached --check`
- optionally full `python -m pytest -q -o 'addopts=' -p no:cacheprovider` if quick enough

## Rollback Point

Pre-run HEAD is `52873c8` and the tree was clean. If aborting S1, revert only the four allowed files/new Phase 369 directory:

- restore `design/codestable/attention.md`
- restore `tests/test_hermes_tavern_codestable_status.py`
- remove `design/codestable/features/2026-06-26-hermes-tavern-phase369-attention-status-sync-through-phase368/design.md`
- remove `design/codestable/features/2026-06-26-hermes-tavern-phase369-attention-status-sync-through-phase368/checklist.yaml`
- remove the new Phase 369 directory if empty

Do not commit, reset, stage, push, or touch unrelated paths unless the parent explicitly authorizes.

## Executor Prompt

You are the S1 executor for Phase 369 attention/status sync through Phase 368 in `/Users/steven/Projects/hermes-tavern`.

Edit only the four allowed files listed in this design. Create only the Phase 369 `design.md` and `checklist.yaml` artifacts. Do not create `acceptance.md`. Do not stage, commit, push, reset, change branches, install packages, start services, or touch runtime/source/plugin/provider/gateway/CLI/config/root docs/README/architecture/roadmap/requirements/compound/build/cache files.

Advance the attention/test status contract exactly from `All phases 1-368 accepted` to `All phases 1-369 accepted`, append `Phase 369 attention status sync through Phase 368`, update the final suffix, update focused test constants, set `phase_range = range(168, 370)`, use live aggregate string `range(168, 370)`, and add split stale guard `stale_aggregate_range_369 = "".join(["range(168, ", "36", "9", ")"])`.

Run the verification commands as feasible and report changed paths plus results. Leave parent verification, acceptance creation, and final checklist completion to S2.

## Read-Only Architect Review Checklist

Post-executor review must return `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES` and verify:

- Phase 369 label appears exactly once in the attention status line and exactly once in `REQUIRED_PHASE_LABELS`.
- Phase 368 label is preserved.
- Phase 121-167 and every explicit Phase 168 through Phase 368 label are preserved.
- Final suffix is exactly `Phase 367 attention status sync through Phase 366, Phase 368 attention status sync through Phase 367, and Phase 369 attention status sync through Phase 368.`
- Test constants match the Phase 369 contract.
- `phase_range = range(168, 370)` and live aggregate string `range(168, 370)` are present.
- Direct stale literal `range(168, 369)` is absent from test source after S1 except split-string guard components.
- `stale_aggregate_range_369` is split and included in the stale tuple.
- Anchored assignment guards and no-discovery-token guards remain.
- No Phase 369 `acceptance.md` exists.
- Checklist is non-final and pending parent verification.
- Changed/untracked paths are limited to the four allowed files.
- No staged files, commits, pushes, resets, branch changes, service starts, or prohibited path edits occurred.
