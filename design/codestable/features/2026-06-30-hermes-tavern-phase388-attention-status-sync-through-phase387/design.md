---
doc_type: feature-design
feature: 2026-06-30-hermes-tavern-phase388-attention-status-sync-through-phase387
title: "Phase 388 attention/status sync through Phase 387"
status: approved
implementation_ready: true
date: "2026-06-30"
owner: company_boost_lane
lane: company_boost_status_sync
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 388 attention/status sync through accepted Phase 387; implementation and parent verification are not final."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase388, company-boost, parent-handoff]
---

# Phase 388 attention/status sync through Phase 387

## Background / Current Status Evidence

Phase 388 is the correct next bounded CodeStable slice.

Evidence confirmed by the read-only Codex architect pass at `/tmp/hermes-tavern-architect_design-1782779438.jsonl`:

- Repository branch is `main` at `d323c77a6292655f40b92daba1746fb08b64e120`; controller preflight showed a clean tree before materializing this slice.
- CodeStable root is `design/codestable`.
- `design/codestable/attention.md` is the startup attention source of truth.
- `design/codestable/attention.md` has one current-status line in `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- That status line currently starts with `Current status (2026-06-18): All phases 1-387 accepted`.
- Its terminal suffix is `Phase 385 attention status sync through Phase 384, Phase 386 attention status sync through Phase 385, and Phase 387 attention status sync through Phase 386.`
- Phase 387 artifacts are complete and accepted: `design.md` is `status: approved`, `checklist.yaml` is `status: accepted`, and `acceptance.md` is `status: accepted`.
- `tests/test_hermes_tavern_codestable_status.py` is pinned to Phase 387: `CURRENT_STATUS_PREFIX` is 1-387, stale prefix/markers are 1-386, `FINAL_STATUS_SUFFIX` ends through Phase 387, and live aggregate range is `range(168, 388)`.
- The focused test preserves anchored assignment-count guards, the current-status section-placement guard, split stale aggregate guards, and self-source guards against `.glob`, `.rglob`, `iterdir`, and `os.walk` discovery tokens.
- No Phase 388 feature directory existed at architect read time.

## Goals

- Materialize the Phase 388 design/checklist pair for a company-boost S1 parent-handoff slice.
- Advance `design/codestable/attention.md` exactly one status tick from 1-387 to 1-388.
- Append `Phase 388 attention status sync through Phase 387` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 387 label.
- Update the focused status regression to guard the Phase 388 live status contract.
- Keep S1 non-final: leave `acceptance.md` absent and reserve final acceptance/status closeout for the parent controller.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No build, root-design, README, architecture, roadmap, requirements, or compound changes.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction boundary change, RP compatibility change, minors-related work, or CSAM-related work.
- No Phase 389 or later work.
- No S2 closeout.
- No `acceptance.md` during S1.

## Allowed Files

Executor S1 may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-30-hermes-tavern-phase388-attention-status-sync-through-phase387/design.md`
- `design/codestable/features/2026-06-30-hermes-tavern-phase388-attention-status-sync-through-phase387/checklist.yaml`

No `acceptance.md` is allowed for this S1 handoff.

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-387 accepted` to `Current status (2026-06-18): All phases 1-388 accepted`.
- Append exactly once in the attention status line: `Phase 388 attention status sync through Phase 387`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 387 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes: `Phase 386 attention status sync through Phase 385, Phase 387 attention status sync through Phase 386, and Phase 388 attention status sync through Phase 387.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-388 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-387 accepted"`
- `STALE_PHASE_MARKER = "1-387"`
- `STALE_PHASE_MARKER_EN_DASH = "1–387"`
- Append `"Phase 388 attention status sync through Phase 387"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 387 required label.
- `FINAL_STATUS_SUFFIX = "Phase 386 attention status sync through Phase 385, Phase 387 attention status sync through Phase 386, and Phase 388 attention status sync through Phase 387."`
- `phase_range = range(168, 389)`
- `aggregate_range = "range(168, 389)"`
- Add `stale_aggregate_range_388 = "".join(["range(168, ", "38", "8", ")"])`.
- Include `stale_aggregate_range_388` in the stale assertion tuple.
- Preserve existing split stale guards, including `stale_aggregate_range_387` and earlier.
- Replace the final split `stale_aggregate_guard` so it builds `range(168, 388)` without embedding that stale literal contiguously anywhere in the test source.
- Do not leave a contiguous stale literal `range(168, 388)` in the test source after the update; the live range is `range(168, 389)`.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive substring counts.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Preserve self-source guards against `.glob`, `.rglob`, `iterdir`, and `os.walk` discovery tokens.
- Add or preserve an exact-once check for the newest label on the attention status line only.

## Structure / Micro-Refactor Boundary

No micro-refactor is scoped. This is a docs/static-test/status-only single-tick update against one long status line and one focused regression test. Creating helpers, changing runtime paths, or touching wider docs would increase risk and violate the bounded slice.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-30-hermes-tavern-phase388-attention-status-sync-through-phase387/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-30-hermes-tavern-phase388-attention-status-sync-through-phase387/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider`
- Static Phase 388 status/scope guard using changed plus untracked files.
- Parent-owned broader pytest gate if requested by the controller.
- `git diff --check`

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior explicit phase label.
- The terminal `and` must move to Phase 388; Phase 387 should become comma-separated.
- `range(168, 388)` becomes stale and must not remain as a contiguous stale literal.
- The existing split stale guard for `range(168, 387)` must remain present in the stale tuple.
- Newest-label exact-once applies only to the attention status line, not to the whole test source.
- Accidentally creating `acceptance.md` would cross the S1/S2 boundary.
- Any runtime, provider, gateway, CLI, config, dependency, build, root-design, README, architecture, roadmap, requirements, compound, safety, minors/CSAM, or provider-bypass change would violate scope.

## S1 Handoff

This design scopes S1 only. Executor should update the allowed docs/test files, leave `acceptance.md` absent, keep checklist/root acceptance statuses non-final with `parent_verification_required: true`, and hand back to the parent/controller for final verification, acceptance creation, commit, and push.
