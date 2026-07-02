---
doc_type: feature-design
feature: 2026-07-02-hermes-tavern-phase414-attention-status-sync-through-phase413
title: "Phase 414 attention/status sync through Phase 413"
status: approved
implementation_ready: true
date: "2026-07-02"
owner: company-boost
lane: company_boost
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 414 attention/status sync through accepted Phase 413; executor implementation is bounded to startup status docs/tests and parent verification remains non-final until controller closeout."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase414, company-boost]
---

# Phase 414 attention/status sync through Phase 413

## Background / Current Status Evidence

Phase 413 is accepted and complete. The read-only architect pass for this company-boost lane inspected `design/codestable/attention.md`, the accepted Phase 412 and Phase 413 artifacts, and `tests/test_hermes_tavern_codestable_status.py`, then selected Phase 414 as the next safe bounded CodeStable slice.

Current evidence before S1:

- Git branch `main` is clean at `0bb7aa7` (`docs: sync tavern status through phase 413`), tracking `origin/main`.
- `design/codestable/attention.md` is the startup attention source of truth and is synced through `All phases 1-413 accepted`.
- Phase 413 artifacts are complete and accepted under `design/codestable/features/2026-07-02-hermes-tavern-phase413-attention-status-sync-through-phase412/`.
- The focused status regression is pinned to the Phase 413 live contract.
- No Phase 414 artifact existed before this slice.

## Goals

- Materialize the Phase 414 design/checklist pair for a company-boost S1 handoff slice.
- Advance `design/codestable/attention.md` exactly one status tick from 1-413 to 1-414.
- Append `Phase 414 attention status sync through Phase 413` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 413 label.
- Update the focused status regression to guard the Phase 414 live status contract.
- Keep S1 non-final: leave `acceptance.md` absent and reserve final acceptance/status closeout for the parent controller.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No build, root-design, README, architecture, roadmap, requirements, compound, review, or cache changes.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes by executor.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction/RP boundary change, minors-related work, or CSAM-related work.
- No Phase 415 or later work.
- No S2 closeout by executor.
- No `acceptance.md` during S1.
- No final checklist, workflow, or acceptance statuses during S1.

## Allowed Files

Controller materialization may create only:

- `design/codestable/features/2026-07-02-hermes-tavern-phase414-attention-status-sync-through-phase413/design.md`
- `design/codestable/features/2026-07-02-hermes-tavern-phase414-attention-status-sync-through-phase413/checklist.yaml`

Executor S1 may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-02-hermes-tavern-phase414-attention-status-sync-through-phase413/checklist.yaml` only to mark S1 implemented/pending parent verification, never final accepted.

No `acceptance.md` is allowed for this S1 handoff.

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-413 accepted` to `Current status (2026-06-18): All phases 1-414 accepted`.
- Append exactly once in the attention status line: `Phase 414 attention status sync through Phase 413`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 413 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes exactly: `Phase 412 attention status sync through Phase 411, Phase 413 attention status sync through Phase 412, and Phase 414 attention status sync through Phase 413.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-414 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-413 accepted"`
- `STALE_PHASE_MARKER = "1-413"`
- `STALE_PHASE_MARKER_EN_DASH = "1–413"`
- Append `"Phase 414 attention status sync through Phase 413"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 413 required label.
- `FINAL_STATUS_SUFFIX = "Phase 412 attention status sync through Phase 411, Phase 413 attention status sync through Phase 412, and Phase 414 attention status sync through Phase 413."`
- `phase_range = range(168, 415)`
- `aggregate_range = "range(168, 415)"`
- Add `stale_aggregate_range_414 = "".join(["range(168, ", "41", "4", ")"])` and include it in the stale assertion tuple.
- Preserve prior split stale guards, including `stale_aggregate_range_413` and earlier.
- Replace the final split guards so they build stale `range(168, 414)` and `range(168, 413)` without embedding either stale literal contiguously in the test source.
- Do not leave contiguous stale literals `range(168, 414)` or `range(168, 413)` in the test source after the update; the live range is `range(168, 415)`.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive substring counts.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Preserve split no-discovery-token guards against `.glob`, `.rglob`, `iterdir`, and `os.walk`.
- Newest-label exact-once applies to the attention status line only. Do not require exact once across the test source because the newest label appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Static Guard Requirements

Controller verification must reject the implementation unless all changed/untracked paths are limited to the two controller-created artifact files plus the two allowed S1 files before acceptance closeout, `acceptance.md` is absent during S1, and no runtime/source/plugin/provider/gateway/CLI/config/dependency/build/root-design/README/architecture/roadmap/requirements/compound/review/cache path changed.

Static checks must verify the exact current-status prefix, stale prefix, stale hyphen/en-dash markers, final suffix, preservation of `Phase 121-167`, preservation of every explicit Phase 168 through Phase 413 label, append of Phase 414 exactly once in the attention status line, current-status section placement, anchored assignment-count guards, no direct stale `range(168, 414)` or `range(168, 413)` literal in the focused test source, no discovery tokens, final newline, and no trailing whitespace.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-02-hermes-tavern-phase414-attention-status-sync-through-phase413 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase414-exec python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static Phase 414 status/scope/final-newline/trailing-whitespace guard.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='`
- `git diff --check`

## Parent acceptance boundary

This phase is S1 implementation only. Parent/controller verification owns acceptance finalization, any acceptance artifact creation, any final accepted checklist/status writeback, and any broader writeback beyond the allowed S1 files.
