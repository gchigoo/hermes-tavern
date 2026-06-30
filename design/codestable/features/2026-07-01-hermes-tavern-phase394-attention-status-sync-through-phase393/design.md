---
doc_type: feature-design
feature: 2026-07-01-hermes-tavern-phase394-attention-status-sync-through-phase393
title: "Phase 394 attention/status sync through Phase 393"
status: approved
implementation_ready: true
date: "2026-07-01"
owner: standard_lane
lane: standard/personal
bounded_phase: "docs/static-test/status-only"
summary: "Approved S1 design for Phase 394 attention/status sync through accepted Phase 393; executor implementation and parent verification remain non-final."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase394, standard-lane]
---

# Phase 394 attention/status sync through Phase 393

## Background / Current Status Evidence

Phase 394 is the correct next bounded CodeStable slice.

Evidence confirmed by controller preflight and the read-only architect pass at `/tmp/hermes-tavern-architect-phase394-20260701-0142.jsonl`:

- Controller preflight reported a clean `main` worktree at `44cf0ce` with `origin/main`.
- Read-only architect confirmed `design/codestable/attention.md` has exactly one current-status line, currently synced through `All phases 1-393 accepted`.
- Phase 393 artifacts are complete and accepted under `design/codestable/features/2026-07-01-hermes-tavern-phase393-attention-status-sync-through-phase392/`.
- `tests/test_hermes_tavern_codestable_status.py` is pinned to Phase 393: current/stale constants are 393/392, live range is `range(168, 394)`, and the split stale guard reaches `stale_aggregate_range_393`.
- Phase 121-167 and explicit Phase 168 through Phase 393 labels are present.
- No Phase 394 feature artifact existed at architect read time.
- The architect pass emitted a bounded `STATUS_SYNC_PHASE_394` plan with `READY: yes` and no failed Codex command records.

## Goals

- Materialize the Phase 394 design/checklist pair for a standard/personal S1 handoff slice.
- Advance `design/codestable/attention.md` exactly one status tick from 1-393 to 1-394.
- Append `Phase 394 attention status sync through Phase 393` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 393 label.
- Update the focused status regression to guard the Phase 394 live status contract.
- Keep S1 non-final: leave `acceptance.md` absent and reserve final acceptance/status closeout for the parent controller.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No build, root-design, README, architecture, roadmap, requirements, or compound changes.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes by executor.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction policy change, RP compatibility change, minors-related work, or CSAM-related work.
- No Phase 395 or later work.
- No S2 closeout by executor.
- No `acceptance.md` during S1.

## Allowed Files

Executor S1 may touch only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-01-hermes-tavern-phase394-attention-status-sync-through-phase393/design.md`
- `design/codestable/features/2026-07-01-hermes-tavern-phase394-attention-status-sync-through-phase393/checklist.yaml`

No `acceptance.md` is allowed for this S1 handoff.

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-393 accepted` to `Current status (2026-06-18): All phases 1-394 accepted`.
- Append exactly once in the attention status line: `Phase 394 attention status sync through Phase 393`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 393 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes exactly: `Phase 392 attention status sync through Phase 391, Phase 393 attention status sync through Phase 392, and Phase 394 attention status sync through Phase 393.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-394 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-393 accepted"`
- `STALE_PHASE_MARKER = "1-393"`
- `STALE_PHASE_MARKER_EN_DASH = "1–393"`
- Append `"Phase 394 attention status sync through Phase 393"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 393 required label.
- `FINAL_STATUS_SUFFIX = "Phase 392 attention status sync through Phase 391, Phase 393 attention status sync through Phase 392, and Phase 394 attention status sync through Phase 393."`
- `phase_range = range(168, 395)`
- `aggregate_range = "range(168, 395)"`
- Add `stale_aggregate_range_394 = "".join(["range(168, ", "39", "4", ")"])`.
- Include `stale_aggregate_range_394` in the stale assertion tuple.
- Preserve prior split stale guards, including `stale_aggregate_range_393` and earlier.
- Replace the final split `stale_aggregate_guard` so it builds stale `range(168, 394)` without embedding contiguous `range(168, 394)` in the test source.
- Do not leave a contiguous stale literal `range(168, 394)` in the test source after the update; the live range is `range(168, 395)`.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive substring counts.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Preserve split no-discovery-token guards against `.glob`, `.rglob`, `iterdir`, and `os.walk`.
- Newest-label exact-once applies to the attention status line only. Do not require exact once across the test source because the newest label appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Static Guard Requirements

Controller verification must reject the implementation unless all changed/untracked paths are exactly the four allowed S1 paths listed above before acceptance closeout, `acceptance.md` is absent during S1, and no runtime/source/provider/gateway/CLI/config/dependency/build/root-design/README/architecture/roadmap/requirements/compound path changed.

Static checks must verify the exact current-status prefix, stale prefix, stale hyphen/en-dash markers, final suffix, preservation of `Phase 121-167`, preservation of every explicit Phase 168 through Phase 393 label, append of Phase 394 exactly once in the attention status line, current-status section placement, anchored assignment-count guards, no direct stale `range(168, 394)` literal in the focused test source, no discovery tokens, final newlines, and no trailing whitespace.

## Structure Health / Microrefactor Decision

No microrefactor is part of this slice. The only planned work is a bounded status-line update, a focused static regression update, and creation of the selected Phase 394 feature artifacts. Changing runtime structure, plugin/provider boundaries, root design, architecture, roadmap, requirements, or compound documents would be outside scope.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase394-attention-status-sync-through-phase393/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase394-attention-status-sync-through-phase393/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static Phase 394 status/scope/final-newline/trailing-whitespace guard using changed plus untracked files.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior explicit phase label.
- The terminal `and` must move to Phase 394; Phase 393 should become comma-separated.
- `range(168, 394)` becomes stale and must not remain as a contiguous stale literal in the focused test source.
- Existing split stale guards, especially `stale_aggregate_range_393`, must remain present in the stale tuple.
- Newest-label exact-once applies only to the attention status line, not to the whole test source.
- Accidentally creating `acceptance.md` in S1 would cross the S1/S2 boundary.
- Any runtime, provider, gateway, CLI, config, dependency, build, root-design, README, architecture, roadmap, requirements, compound, safety, minors/CSAM, or provider-bypass change would violate scope.

## S1 Handoff

This design scopes S1 only. Executor should update the allowed docs/test files, leave `acceptance.md` absent, keep checklist/root acceptance statuses non-final with `parent_verification_required: true`, and hand back to the parent/controller for final verification, acceptance creation, commit, and push.
