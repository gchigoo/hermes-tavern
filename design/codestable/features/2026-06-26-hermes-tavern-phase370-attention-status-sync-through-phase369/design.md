---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase370-attention-status-sync-through-phase369
title: "Phase 370 attention/status sync through Phase 369"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 370 attention/status sync through accepted Phase 369."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase370, company-boost, parent-handoff]
---

# Phase 370 attention/status sync through Phase 369

## Background / Current State

Read-only architect inspection confirmed the safe next bounded slice is Phase 370.

Inspected baseline:

- Pre-run HEAD: `3e99754ff0ad342859fe92570f2907f8b7d20f6a` on `main`, clean.
- `design/codestable/features/2026-06-26-hermes-tavern-phase369-attention-status-sync-through-phase368/design.md` is `status: approved`.
- `design/codestable/features/2026-06-26-hermes-tavern-phase369-attention-status-sync-through-phase368/checklist.yaml` is accepted and parent-verified.
- `design/codestable/features/2026-06-26-hermes-tavern-phase369-attention-status-sync-through-phase368/acceptance.md` exists and is accepted.
- `design/codestable/features/2026-06-26-hermes-tavern-phase370-attention-status-sync-through-phase369/` is absent before S1.
- Current status prefix/text: `Current status (2026-06-18): All phases 1-369 accepted`.
- Current terminal suffix: `Phase 367 attention status sync through Phase 366, Phase 368 attention status sync through Phase 367, and Phase 369 attention status sync through Phase 368.`
- Target status prefix/text: `Current status (2026-06-18): All phases 1-370 accepted`.
- Target terminal suffix: `Phase 368 attention status sync through Phase 367, Phase 369 attention status sync through Phase 368, and Phase 370 attention status sync through Phase 369.`
- `tests/test_hermes_tavern_codestable_status.py` currently pins Phase 369 with `CURRENT_STATUS_PREFIX`, `FINAL_STATUS_SUFFIX`, `phase_range = range(168, 370)`, and live aggregate string `range(168, 370)`.

Range note: Phase 370 must advance the live range to `range(168, 371)` and add a split stale guard for the previous live aggregate `range(168, 370)` without embedding that stale literal contiguously in the test source.

## Goals

- Materialize the Phase 370 design/checklist artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-369 to 1-370.
- Append `Phase 370 attention status sync through Phase 369` exactly once.
- Update the focused status regression to guard the Phase 370 live status contract.
- Preserve `Phase 121-167 novel project layer + metadata + JSON export for all entity types`.
- Preserve every explicit Phase 168 through Phase 369 label, including punctuation and the exact Phase 369 label.
- Leave S1 in non-final parent-verification handoff state.

## Non-Goals

- No `acceptance.md` creation during executor S1.
- No Phase 371 or later work.
- No runtime/source/plugin/provider/gateway/CLI/config/network/dependency/build/cache/service lifecycle changes.
- No root docs, README, architecture, roadmap, requirements, compound, or reference edits.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No provider safety/content behavior changes.
- Adult-fiction/RP compatibility remains unchanged; no minors-related behavior changes.
- No package installs, service starts, staging, commits, pushes, resets, or branch changes.

## Allowed / Protected Scope

Executor S1 may edit only exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase370-attention-status-sync-through-phase369/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase370-attention-status-sync-through-phase369/checklist.yaml`

Creating the Phase 370 feature directory solely to hold `design.md` and `checklist.yaml` is allowed.

Protected/prohibited paths include:

- `design/codestable/features/2026-06-26-hermes-tavern-phase370-attention-status-sync-through-phase369/acceptance.md` during executor S1
- all other `design/codestable/features/**`
- `design/codestable/architecture/**`
- `design/codestable/compound/**`
- `design/codestable/roadmap/**`
- `design/codestable/requirements/**`
- `design/codestable/reference/**`
- `design/codestable/reviews/**`
- `src/**`
- `plugins/**`
- `tests/**` except `tests/test_hermes_tavern_codestable_status.py`
- `README.md`, `CHANGELOG.md`, `SECURITY.md`, `CONTRIBUTING.md`, `SUPPORT.md`
- `pyproject.toml`, `requirements-test.txt`, `conftest.py`, `smoke_turn_controls.py`
- `patches/**`, `.github/**`, `.git/**`, `build/**`, `.pytest_cache/**`, `__pycache__/**`, `tests/__pycache__/**`, `plugins/__pycache__/**`
- `run_agent.py`, `cli.py`, `gateway/run.py` if present

## Exact Mechanical Changes

### attention.md

- Change `All phases 1-369 accepted` to `All phases 1-370 accepted`.
- Append `Phase 370 attention status sync through Phase 369` exactly once.
- Move the terminal `and` from Phase 369 to Phase 370.
- Final suffix after S1 must be exactly: `Phase 368 attention status sync through Phase 367, Phase 369 attention status sync through Phase 368, and Phase 370 attention status sync through Phase 369.`
- Preserve all prior Phase labels and punctuation exactly.

### tests/test_hermes_tavern_codestable_status.py

Set constants exactly:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-370 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-369 accepted"`
- `STALE_PHASE_MARKER = "1-369"`
- `STALE_PHASE_MARKER_EN_DASH = "1–369"`
- `FINAL_STATUS_SUFFIX = "Phase 368 attention status sync through Phase 367, Phase 369 attention status sync through Phase 368, and Phase 370 attention status sync through Phase 369."`

Required label handling:

- Append `"Phase 370 attention status sync through Phase 369"` to `REQUIRED_PHASE_LABELS` exactly once.
- Preserve every prior label, including `Phase 168` through `Phase 369`, with punctuation unchanged.

Range and stale aggregate handling:

- Set `phase_range = range(168, 371)`.
- Use live aggregate string `"range(168, 371)"` for every live aggregate assertion.
- Add `stale_aggregate_range_370 = "".join(["range(168, ", "37", "0", ")"])`.
- Include `stale_aggregate_range_370` in the stale assertion tuple.
- Ensure direct stale range literal `range(168, 370)` is absent from test source after S1 except via split-string guard components.
- Preserve single anchored assignment guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.
- Preserve no direct discovery token guards for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk`.

## Checklist State After S1

After executor S1, checklist must remain non-final:

- `status: implemented`
- `workflow_status: pending_parent_verification`
- `acceptance_state: pending_parent_verification`
- `parent_verification_required: true`
- `worker_commit_or_push_performed: false`
- `acceptance_artifact: null`

S1 checks may be marked completed. S2 parent verification checks must remain pending unless the controller explicitly performs acceptance closeout later.

## Verification Commands

Run from repository root:

- `export HERMES_HOME=/Users/steven/.hermes`
- `unset HERMES_SESSION_KEY HERMES_SESSION_ID`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-26-hermes-tavern-phase370-attention-status-sync-through-phase369/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-26-hermes-tavern-phase370-attention-status-sync-through-phase369/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `test ! -e design/codestable/features/2026-06-26-hermes-tavern-phase370-attention-status-sync-through-phase369/acceptance.md` after executor S1
- Static guard assertions: branch/head unchanged, no staged files, changed/untracked paths subset of S1 allowlist, all four allowed files exist, no Phase 370 acceptance artifact after executor S1, exactly one current status line, Phase 370 prefix/suffix/label correct, Phase 121-167 and Phase 168-369 preserved, stale markers point to 1-369/1–369, anchored `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX` assignment guards present exactly once, `phase_range = range(168, 371)` present, live aggregate `range(168, 371)` present, direct stale aggregate `range(168, 370)` absent from test source, split `stale_aggregate_range_370` included in stale tuple, no direct discovery tokens in test source, checklist non-final.
- `git diff --check`
- `git diff --cached --check`
- Optional if quick: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`

## Executor Prompt

You are the S1 executor for Phase 370 attention/status sync through Phase 369 in `/Users/steven/Projects/hermes-tavern`.

Edit only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase370-attention-status-sync-through-phase369/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase370-attention-status-sync-through-phase369/checklist.yaml`

Create only the Phase 370 `design.md` and `checklist.yaml` artifacts. Do not create `acceptance.md` unless a later controller explicitly performs acceptance closeout. Do not stage, commit, push, reset, change branches, install packages, start services, or touch runtime/source/plugin/provider/gateway/CLI/config/root docs/README/architecture/roadmap/requirements/compound/reference/build/cache files.

Advance the attention/test status contract exactly from `All phases 1-369 accepted` to `All phases 1-370 accepted`, append `Phase 370 attention status sync through Phase 369`, update the final suffix, update focused test constants, set `phase_range = range(168, 371)`, use live aggregate string `range(168, 371)`, and add split stale guard `stale_aggregate_range_370 = "".join(["range(168, ", "37", "0", ")"])`.

Run the verification commands as feasible and report changed paths plus results. Leave parent verification, acceptance creation, and final checklist completion to S2.

## Read-Only Architect Review Checklist

Post-executor review must return `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES` and verify:

- Phase 370 label appears exactly once in the attention status line and exactly once in `REQUIRED_PHASE_LABELS`.
- Phase 369 label is preserved.
- Phase 121-167 and every explicit Phase 168 through Phase 369 label are preserved.
- Final suffix is exactly `Phase 368 attention status sync through Phase 367, Phase 369 attention status sync through Phase 368, and Phase 370 attention status sync through Phase 369.`
- Test constants match the Phase 370 contract.
- `phase_range = range(168, 371)` and live aggregate string `range(168, 371)` are present.
- Direct stale literal `range(168, 370)` is absent from test source after S1 except split-string guard components.
- `stale_aggregate_range_370` is split and included in the stale tuple.
- Anchored assignment guards and no-discovery-token guards remain.
- No Phase 370 `acceptance.md` exists unless controller S2 explicitly drafted it.
- Checklist is non-final and pending parent verification unless controller S2 explicitly finalized it.
- Changed/untracked paths are limited to allowed files plus any controller-owned Phase 370 acceptance artifact if S2 closeout is explicitly drafted.
- No staged files, commits, pushes, resets, branch changes, service starts, or prohibited path edits occurred.
