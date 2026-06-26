---
doc_type: feature-design
feature: 2026-06-26-hermes-tavern-phase367-attention-status-sync-through-phase366
title: "Phase 367 attention/status sync through Phase 366"
status: approved
implementation_ready: true
date: "2026-06-26"
owner: standard_lane
lane: standard
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 367 attention/status sync through accepted Phase 366."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase367]
---

# Phase 367 attention/status sync through Phase 366

## Background / Current Status

Phase 366 is accepted:

`design/codestable/features/2026-06-26-hermes-tavern-phase366-attention-status-sync-through-phase365/acceptance.md`

Inspected baseline:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-366 accepted`.
- Terminal suffix is `Phase 364 attention status sync through Phase 363, Phase 365 attention status sync through Phase 364, and Phase 366 attention status sync through Phase 365.`
- `tests/test_hermes_tavern_codestable_status.py` has `CURRENT_STATUS_PREFIX` pinned to Phase 366.
- The focused status test currently has stale prefix and markers for Phase 365.
- The focused status test currently uses `phase_range = range(168, 367)` and live aggregate string `range(168, 367)`.
- The focused status test already includes the split stale aggregate guard for `range(168, 366)`.
- The Phase 367 feature directory is not present before S1.

Range note: Phase 367 must advance the live range to `range(168, 368)` and add a split stale guard for `range(168, 367)`.

## Goals

- Materialize the Phase 367 design/checklist artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-366 to 1-367.
- Append `Phase 367 attention status sync through Phase 366` exactly once.
- Update the focused status regression to guard the Phase 367 live status contract.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 366 label; add Phase 367 exactly once.
- Leave the checklist in non-final S1 handoff state for parent verification.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/build updates.
- No root docs, architecture, roadmap, requirements, or compound updates.
- No service lifecycle commands, cache artifacts, staging, commits, or pushes.
- No `acceptance.md` creation during executor S1.
- No final accepted/completed/passed closeout during executor S1.
- No Phase 368 work.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No provider-safety, content, RP, adult-fiction behavior, or minor-related behavior changes.

## S1/S2 Boundary

Executor S1 may edit only exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase367-attention-status-sync-through-phase366/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase367-attention-status-sync-through-phase366/checklist.yaml`

Executor S1 must not create `acceptance.md`, stage, commit, push, touch Phase 368, or touch prohibited runtime/source/plugin/provider/gateway/CLI/config/dependency/root docs/architecture/roadmap/requirements/compound/build/service lifecycle/cache paths.

Executor S1 may leave checklist S1 step/check statuses as `completed` only for completed executor work, with top-level `status: implemented`, `workflow_status: pending_parent_verification`, and `acceptance_state: pending_parent_verification`.

Controller S2 owns verification, any future `acceptance.md` creation, and final checklist status updates after verification.

## Expected S1 Mechanical Changes

### attention.md

- `All phases 1-366 accepted` -> `All phases 1-367 accepted`
- Move `and` from Phase 366 to Phase 367.
- Append `Phase 367 attention status sync through Phase 366` after Phase 366.
- Final suffix must be `Phase 365 attention status sync through Phase 364, Phase 366 attention status sync through Phase 365, and Phase 367 attention status sync through Phase 366.`

### test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX`: `1-366` -> `1-367`
- `STALE_STATUS_PREFIX`: `1-365` -> `1-366`
- `STALE_PHASE_MARKER`: `1-365` -> `1-366`
- `STALE_PHASE_MARKER_EN_DASH`: `1–365` -> `1–366`
- Add `"Phase 367 attention status sync through Phase 366"` to `REQUIRED_PHASE_LABELS` exactly once; preserve every existing Phase 168 through Phase 366 label.
- Preserve the existing `Phase 121-167` guard.
- `FINAL_STATUS_SUFFIX`: `Phase 365 attention status sync through Phase 364, Phase 366 attention status sync through Phase 365, and Phase 367 attention status sync through Phase 366.`
- `phase_range`: `range(168, 367)` -> `range(168, 368)`
- Live `aggregate_range`: `"range(168, 367)"` -> `"range(168, 368)"`
- Add split stale aggregate guard `stale_aggregate_range_367 = "".join(["range(168, ", "36", "7", ")"])`
- Include `stale_aggregate_range_367` in the stale range assertion tuple.
- Do not leave a contiguous literal `range(168, 367)` in test source after S1; the stale guard must be split and the live aggregate must be `range(168, 368)`.
- Keep anchored single-assignment guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.
- Preserve existing no-discovery-token guards.

## Required Phase Labels And Final Suffix

Required label coverage after S1:

- Attention status keeps `Phase 121-167 novel project layer + metadata + JSON export for all entity types`.
- `REQUIRED_PHASE_LABELS` preserves every existing explicit Phase 168 through Phase 366 label.
- `REQUIRED_PHASE_LABELS` adds `Phase 367 attention status sync through Phase 366` exactly once.
- Final attention suffix is exactly `Phase 365 attention status sync through Phase 364, Phase 366 attention status sync through Phase 365, and Phase 367 attention status sync through Phase 366.`

## Stale Range Guards

- Live aggregate string must be `range(168, 368)`.
- Live phase range must be `phase_range = range(168, 368)`.
- Stale aggregate guard for the previous live range must be split as `stale_aggregate_range_367 = "".join(["range(168, ", "36", "7", ")"])`.
- `stale_aggregate_range_367` must be included in the stale assertion tuple.
- Test source must not contain contiguous stale literal `range(168, 367)` after S1.
- Anchored single assignment guards must remain for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`.

## Task Plan

1. Create `design/codestable/features/2026-06-26-hermes-tavern-phase367-attention-status-sync-through-phase366/` with this `design.md` and the paired `checklist.yaml`.
2. Update the single attention current-status line from Phase 366 to Phase 367.
3. Append the Phase 367 label and move the terminal `and` so the suffix ends with Phase 365, Phase 366, and Phase 367.
4. Update the focused status test constants, required labels, final suffix, live range, live aggregate string, and split stale range guard.
5. Run YAML/frontmatter validation, Python compile, focused pytest, static status/range guard, changed-path guard, and diff checks.
6. Leave S2 verification and any future acceptance finalization to the parent.

## Verification Commands

```bash
export HERMES_HOME=/Users/steven/.hermes
unset HERMES_SESSION_KEY HERMES_SESSION_ID
PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-26-hermes-tavern-phase367-attention-status-sync-through-phase366/design.md --require doc_type --require status --require feature --require implementation_ready
PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-26-hermes-tavern-phase367-attention-status-sync-through-phase366/checklist.yaml --yaml-only
PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 python /tmp/hermes-tavern-phase367-static-guard.py
test ! -e design/codestable/features/2026-06-26-hermes-tavern-phase367-attention-status-sync-through-phase366/acceptance.md
git diff --check
git diff --cached --check
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider
git status --short --branch
```

The static guard must compare changed + untracked paths against the four-file S1 allowlist, scan new untracked artifacts for trailing whitespace/final newline, assert the attention/test Phase 367 contract, and assert no protected runtime/source/provider/gateway/config/root-design/architecture/roadmap/requirements/compound/build paths changed.

## Executor Prompt

```markdown
You are the S1 executor for Phase 367 attention/status sync through Phase 366 in `/Users/steven/Projects/hermes-tavern`.

Edit only these files:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-26-hermes-tavern-phase367-attention-status-sync-through-phase366/design.md`
- `design/codestable/features/2026-06-26-hermes-tavern-phase367-attention-status-sync-through-phase366/checklist.yaml`

Create the Phase 367 feature directory and write the provided `design.md` and `checklist.yaml`. Then advance the attention/test status contract exactly from `All phases 1-366 accepted` to `All phases 1-367 accepted`, append `Phase 367 attention status sync through Phase 366`, update the final suffix, update focused test constants, set `phase_range = range(168, 368)`, use live aggregate string `range(168, 368)`, and add split stale guard `stale_aggregate_range_367 = "".join(["range(168, ", "36", "7", ")"])`.

Do not create `acceptance.md`. Do not stage, commit, or push. Do not touch runtime/source/plugin/provider/gateway/config/root docs/architecture/roadmap/requirements/compound/build/cache/service lifecycle files, `run_agent.py`, `cli.py`, or `gateway/run.py`.

Run the verification commands from the checklist as feasible and report changed paths plus results. Leave parent verification, acceptance creation, and final checklist completion to S2.
```

## Read-Only Architect Review Checklist

The post-executor read-only review must return `VERDICT: PASS` or `VERDICT: REQUEST_CHANGES` and cover each item below:

- Exact labels: `Phase 367 attention status sync through Phase 366` appears exactly once in the attention status line, appears in `REQUIRED_PHASE_LABELS`, and Phase 121-167 plus every explicit Phase 168 through Phase 366 label is preserved.
- Exact final suffix: `Phase 365 attention status sync through Phase 364, Phase 366 attention status sync through Phase 365, and Phase 367 attention status sync through Phase 366.`
- Single anchored assignments: exactly one top-level `CURRENT_STATUS_PREFIX =` and exactly one top-level `FINAL_STATUS_SUFFIX =` in `tests/test_hermes_tavern_codestable_status.py`.
- Stale status guard: `STALE_STATUS_PREFIX`, `STALE_PHASE_MARKER`, and `STALE_PHASE_MARKER_EN_DASH` point at 1-366; the direct stale live aggregate literal `range(168, 367)` is absent from the test source except via split-string guard components.
- Aggregate range: live `phase_range = range(168, 368)` and live aggregate string `range(168, 368)` are present.
- Synchronization: `design/codestable/attention.md` and the focused status test agree on `All phases 1-367 accepted`.
- S1 boundary: no `acceptance.md` exists for Phase 367, checklist remains non-final with `parent_verification_required: true`, and parent/controller verification remains pending.
- Protected scope: changed/untracked files are limited to the four S1 allowed files; no runtime/source/plugin/provider/gateway/config/root-design/README/architecture/roadmap/requirements/compound/build/cache files changed.
- Git hygiene: no staging, commit, or push occurred.
