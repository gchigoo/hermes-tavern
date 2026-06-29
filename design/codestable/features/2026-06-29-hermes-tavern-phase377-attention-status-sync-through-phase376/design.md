---
doc_type: feature-design
feature: 2026-06-29-hermes-tavern-phase377-attention-status-sync-through-phase376
title: "Phase 377 attention/status sync through Phase 376"
status: approved
implementation_ready: true
date: "2026-06-29"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready: Phase 377 attention/status sync through accepted Phase 376."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase377, company-boost, parent-handoff]
---

# Phase 377 attention/status sync through Phase 376

## Background / Current State

- Baseline observed by controller: branch `main`, HEAD `3dc6372`, clean tree.
- Phase 376 is accepted: `design/codestable/features/2026-06-26-hermes-tavern-phase376-attention-status-sync-through-phase375/acceptance.md`.
- No Phase 377 feature directory existed before this slice.
- `design/codestable/attention.md` current status line is under `### 其他`, after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Current attention prefix: `Current status (2026-06-18): All phases 1-376 accepted`.
- Current terminal suffix: `Phase 374 attention status sync through Phase 373, Phase 375 attention status sync through Phase 374, and Phase 376 attention status sync through Phase 375.`
- Focused status test currently pins Phase 376, stale guards Phase 375, required labels through Phase 376, `phase_range = range(168, 377)`, aggregate string `range(168, 377)`, and split stale guard for `range(168, 376)`.

## Goals

- Advance `attention.md` exactly one status tick from 1-376 to 1-377.
- Append `Phase 377 attention status sync through Phase 376` exactly once.
- Preserve `Phase 121-167` and all explicit Phase 168 through Phase 376 labels.
- Update focused status regression constants, labels, suffix, live range, aggregate string, and stale split guard for Phase 377.
- Leave S1 non-final and pending parent verification until controller gates pass.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/root design/architecture/roadmap/requirements/compound/build/cache/service lifecycle changes.
- No Phase 378 or later work.
- No `acceptance.md` during executor S1.
- No stage, commit, push, reset, package install, network, or service start.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction/RP boundary change, minors-related work, or CSAM-related work.

## Allowed Scope

Executor S1 may edit only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-29-hermes-tavern-phase377-attention-status-sync-through-phase376/design.md` only if needed to keep metadata honest
- `design/codestable/features/2026-06-29-hermes-tavern-phase377-attention-status-sync-through-phase376/checklist.yaml` only if needed to keep metadata honest

## Exact Status Contract

- `attention.md`: `All phases 1-376 accepted` -> `All phases 1-377 accepted`.
- Append exactly: `Phase 377 attention status sync through Phase 376`.
- Preserve prior labels including Phase 376.
- Final suffix must be: `Phase 375 attention status sync through Phase 374, Phase 376 attention status sync through Phase 375, and Phase 377 attention status sync through Phase 376.`

Focused test changes:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-377 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-376 accepted"`
- `STALE_PHASE_MARKER = "1-376"`
- `STALE_PHASE_MARKER_EN_DASH = "1–376"`
- Append `"Phase 377 attention status sync through Phase 376"` to `REQUIRED_PHASE_LABELS`.
- `FINAL_STATUS_SUFFIX` equals the Phase 375/376/377 suffix above.
- `phase_range = range(168, 378)`
- `aggregate_range = "range(168, 378)"`
- Add `stale_aggregate_range_377 = "".join(["range(168, ", "37", "7", ")"])`.
- Include `stale_aggregate_range_377` in the stale assertion tuple.
- Do not leave contiguous stale literal `range(168, 377)` in the test source except split pieces.

## Verification Gates

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-29-hermes-tavern-phase377-attention-status-sync-through-phase376/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-29-hermes-tavern-phase377-attention-status-sync-through-phase376/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static source/status guard confirming prefix, suffix, labels, stale literals, and allowed paths.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider` if feasible.
- `git diff --check`
- Changed/untracked whitespace/final-newline guard.

## Parent-Controller S2 Ownership

- This phase is a company-boost status-sync single-tick slice.
- Executor S1 must leave `acceptance.md` absent and avoid stage/commit/push.
- Worker/controller may create `acceptance.md` and finalize checklist S2 only after real verification gates pass.
- No architecture, requirements, roadmap, root-design, runtime, or plugin writeback is needed.
