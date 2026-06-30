---
doc_type: feature-design
feature: 2026-06-30-hermes-tavern-phase390-attention-status-sync-through-phase389
title: "Phase 390 attention/status sync through Phase 389"
status: approved
implementation_ready: true
date: "2026-06-30"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 390 attention/status sync through accepted Phase 389; executor implementation and parent verification remain non-final."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase390, company-boost, parent-handoff]
---

# Phase 390 attention/status sync through Phase 389

## Background / Current Status Evidence

Phase 390 is the correct next bounded CodeStable slice.

Evidence confirmed by the read-only architect pass at `/tmp/hermes-tavern-architect_design-20260630-103605.jsonl`:

- Controller preflight `git status --short --branch` confirmed `## main...origin/main` before this artifact pair was materialized.
- CodeStable root is `design/codestable`.
- `design/codestable/attention.md` is the startup attention source of truth.
- `design/codestable/attention.md` has one current-status line in `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- That status line currently starts with `Current status (2026-06-18): All phases 1-389 accepted`.
- Its terminal suffix is `Phase 387 attention status sync through Phase 386, Phase 388 attention status sync through Phase 387, and Phase 389 attention status sync through Phase 388.`
- Phase 389 artifacts are complete and accepted: `design.md` is approved, `checklist.yaml` is accepted, and `acceptance.md` is accepted under `design/codestable/features/2026-06-30-hermes-tavern-phase389-attention-status-sync-through-phase388/`.
- `tests/test_hermes_tavern_codestable_status.py` is pinned to Phase 389: `CURRENT_STATUS_PREFIX` is 1-389, stale prefix/markers are 1-388, `FINAL_STATUS_SUFFIX` ends through Phase 389, and live aggregate range is `range(168, 390)`.
- The focused test preserves anchored assignment-count guards, the current-status section-placement guard, split stale aggregate guards, and self-source guards against `.glob`, `.rglob`, `iterdir`, and `os.walk` discovery tokens.
- No Phase 390 feature artifact existed at architect read time.

## Goals

- Materialize the Phase 390 design/checklist pair for a company-boost S1 parent-handoff slice.
- Advance `design/codestable/attention.md` exactly one status tick from 1-389 to 1-390.
- Append `Phase 390 attention status sync through Phase 389` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 389 label.
- Update the focused status regression to guard the Phase 390 live status contract.
- Keep S1 non-final: leave `acceptance.md` absent and reserve final acceptance/status closeout for the parent controller.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No build, root-design, README, architecture, roadmap, requirements, or compound changes.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction boundary change, RP compatibility change, minors-related work, or CSAM-related work.
- No Phase 391 or later work.
- No S2 closeout.
- No `acceptance.md` during S1.

## Allowed Files

Executor S1 may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-30-hermes-tavern-phase390-attention-status-sync-through-phase389/design.md`
- `design/codestable/features/2026-06-30-hermes-tavern-phase390-attention-status-sync-through-phase389/checklist.yaml`

No `acceptance.md` is allowed for this S1 handoff.

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-389 accepted` to `Current status (2026-06-18): All phases 1-390 accepted`.
- Append exactly once in the attention status line: `Phase 390 attention status sync through Phase 389`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 389 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes: `Phase 388 attention status sync through Phase 387, Phase 389 attention status sync through Phase 388, and Phase 390 attention status sync through Phase 389.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-390 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-389 accepted"`
- `STALE_PHASE_MARKER = "1-389"`
- `STALE_PHASE_MARKER_EN_DASH = "1–389"`
- Append `"Phase 390 attention status sync through Phase 389"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 389 required label.
- `FINAL_STATUS_SUFFIX = "Phase 388 attention status sync through Phase 387, Phase 389 attention status sync through Phase 388, and Phase 390 attention status sync through Phase 389."`
- `phase_range = range(168, 391)`
- `aggregate_range = "range(168, 391)"`
- Add `stale_aggregate_range_390 = "".join(["range(168, ", "39", "0", ")"])`.
- Include `stale_aggregate_range_390` in the stale assertion tuple.
- Preserve prior split stale guards, including `stale_aggregate_range_389` and earlier.
- Replace the final split `stale_aggregate_guard` so it builds stale `range(168, 390)` without embedding contiguous `range(168, 390)` in the test source.
- Do not leave a contiguous stale literal `range(168, 390)` in the test source after the update; the live range is `range(168, 391)`.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive substring counts.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Preserve split no-discovery-token guards against `.glob`, `.rglob`, `iterdir`, and `os.walk`.
- Newest-label exact-once applies to the attention status line only. Do not require exact once across the test source because the newest label appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Static Guard Requirements

Controller verification must reject the implementation unless all changed/untracked paths are exactly the four allowed S1 paths listed above, `acceptance.md` is absent, and no runtime/source/provider/gateway/CLI/config/dependency/build/root-design/README/architecture/roadmap/requirements/compound path changed.

Static checks must verify the exact current-status prefix, stale prefix, stale hyphen/en-dash markers, final suffix, preservation of `Phase 121-167`, preservation of every explicit Phase 168 through Phase 389 label, append of Phase 390 exactly once in the attention status line, current-status section placement, anchored assignment-count guards, no direct stale `range(168, 390)` literal in the focused test source, and no discovery tokens.

## Structure / Micro-Refactor Boundary

No micro-refactor is scoped. This is a docs/static-test/status-only single-tick update against one long status line and one focused regression test. Creating helpers, changing runtime paths, or touching wider docs would increase risk and violate the bounded slice.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-30-hermes-tavern-phase390-attention-status-sync-through-phase389/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-30-hermes-tavern-phase390-attention-status-sync-through-phase389/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static Phase 390 status/scope guard using changed plus untracked files.
- Parent-owned broader pytest gate if requested by the controller.
- `git diff --check`

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior explicit phase label.
- The terminal `and` must move to Phase 390; Phase 389 should become comma-separated.
- `range(168, 390)` becomes stale and must not remain as a contiguous stale literal in the focused test source.
- Existing split stale guards, especially `stale_aggregate_range_389`, must remain present in the stale tuple.
- Newest-label exact-once applies only to the attention status line, not to the whole test source.
- Accidentally creating `acceptance.md` would cross the S1/S2 boundary.
- Any runtime, provider, gateway, CLI, config, dependency, build, root-design, README, architecture, roadmap, requirements, compound, safety, minors/CSAM, or provider-bypass change would violate scope.

## S1 Handoff

This design scopes S1 only. Executor should update the allowed docs/test files, leave `acceptance.md` absent, keep checklist/root acceptance statuses non-final with `parent_verification_required: true`, and hand back to the parent/controller for final verification, acceptance creation, commit, and push.
