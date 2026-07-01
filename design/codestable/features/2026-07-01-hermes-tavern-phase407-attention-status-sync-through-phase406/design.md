---
doc_type: feature-design
feature: 2026-07-01-hermes-tavern-phase407-attention-status-sync-through-phase406
title: "Phase 407 attention/status sync through Phase 406"
status: approved
implementation_ready: true
date: "2026-07-01"
owner: company_boost_lane
lane: company-boost/uncommitted
bounded_phase: "docs/static-test/status-only"
summary: "Approved design for Phase 407 attention/status sync through accepted Phase 406; S1 worker handoff only, pending parent verification, with no executor commit or push."
parent_verification_status: pending_parent_verification
acceptance_state: pending_parent_verification
parent_verification_required: true
worker_commit_or_push_performed: false
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase407, company-boost]
---

# Phase 407 attention/status sync through Phase 406

## Background / Current Status Evidence

Phase 406 is already accepted and complete. The current CodeStable attention status line is synced through `All phases 1-406 accepted`, Phase 406 artifacts are present and accepted, Phase 405 artifacts are accepted, the focused status regression is pinned to the Phase 406 contract, and no Phase 407 feature directory existed before the read-only architect pass.

Therefore Phase 407 is the next safe bounded CodeStable slice.

## Goals

- Materialize the Phase 407 design/checklist artifact set for an S1 company-boost dirty-tree handoff.
- Advance `design/codestable/attention.md` exactly one status tick from 1-406 to 1-407.
- Append `Phase 407 attention status sync through Phase 406` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 406 label.
- Update the focused status regression to guard the Phase 407 live status contract.
- Record truthful S1 worker evidence while leaving parent/controller verification pending; executor does not stage, commit, or push.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No root-design, README, architecture, roadmap, requirements, compound, review, build, or cache changes.
- No acceptance.md creation during S1.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction policy change, RP compatibility change, minors-related work, or CSAM-related work.
- No parent/controller verification completion inside this executor slice.
- No Phase 408 or later work.

## Allowed Files

Only these files are in scope:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-01-hermes-tavern-phase407-attention-status-sync-through-phase406/design.md`
- `design/codestable/features/2026-07-01-hermes-tavern-phase407-attention-status-sync-through-phase406/checklist.yaml`

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-406 accepted` to `Current status (2026-06-18): All phases 1-407 accepted`.
- Append exactly once in the attention status line: `Phase 407 attention status sync through Phase 406`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 406 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes exactly: `Phase 405 attention status sync through Phase 404, Phase 406 attention status sync through Phase 405, and Phase 407 attention status sync through Phase 406.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-407 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-406 accepted"`
- `STALE_PHASE_MARKER = "1-406"`
- `STALE_PHASE_MARKER_EN_DASH = "1–406"`
- Append `"Phase 407 attention status sync through Phase 406"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 406 required label.
- `FINAL_STATUS_SUFFIX = "Phase 405 attention status sync through Phase 404, Phase 406 attention status sync through Phase 405, and Phase 407 attention status sync through Phase 406."`
- `phase_range = range(168, 408)`
- `aggregate_range = "range(168, 408)"`
- Add `stale_aggregate_range_407 = "".join(["range(168, ", "40", "7", ")"])`.
- Include `stale_aggregate_range_407` in the stale assertion tuple.
- Preserve prior split stale guards, including `stale_aggregate_range_406`, `stale_aggregate_range_405`, `stale_aggregate_range_404`, and earlier.
- Replace the final split `stale_aggregate_guard` so it builds stale `range(168, 407)` without embedding contiguous `range(168, 407)` in the test source after the update; the live range is `range(168, 408)`.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive substring counts.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Preserve split no-discovery-token guards against `.glob`, `.rglob`, `iterdir`, and `os.walk`.
- Newest-label exact-once applies to the attention status line only. Do not require exact once across the test source because the newest label appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Static Guard Requirements

Parent/controller verification must reject the implementation unless all changed/untracked paths are exactly the four allowed Phase 407 paths listed above and no runtime/source/plugin/provider/gateway/CLI/config/dependency/root-design/README/architecture/roadmap/requirements/compound/review/build/cache path changed.

Static checks must verify the exact current-status prefix, stale prefix, stale hyphen/en-dash markers, final suffix, preservation of `Phase 121-167`, preservation of every explicit Phase 168 through Phase 406 label, append of Phase 407 exactly once in the attention status line, current-status section placement, anchored assignment-count guards, no direct stale `range(168, 407)` literal in the focused test source, no discovery tokens, no Phase 407 acceptance.md in S1, final newlines, and no trailing whitespace.

## Structure Health / Microrefactor Decision

No microrefactor is part of this slice. The only planned work is a bounded status-line update, a focused static regression update, and creation of the selected Phase 407 feature design/checklist artifacts. Changing runtime structure, plugin/provider boundaries, root design, architecture, roadmap, requirements, compound documents, or acceptance artifacts would be outside scope.

## Verification Commands

Worker-side execution in S1 may run the YAML validators, compile check, focused status pytest, static guard, and `git diff --check`; parent/controller verification remains pending after this executor handoff and is responsible for full-suite verification and final acceptance decisions.

Recommended worker/controller gates:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-01-hermes-tavern-phase407-attention-status-sync-through-phase406 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase407 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static allowed-path/status/scope/final-newline/trailing-whitespace guard over `git diff --name-only` plus `git ls-files --others --exclude-standard`.
- `git diff --check`

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior explicit phase label.
- The terminal `and` must move to Phase 407; Phase 406 should become comma-separated.
- `range(168, 407)` becomes stale and must not remain as a contiguous stale literal in the focused test source.
- Existing split stale guards, especially `stale_aggregate_range_406`, must remain present in the stale tuple.
- Newest-label exact-once applies only to the attention status line, not to the whole test source.
- Any runtime, provider, gateway, CLI, config, dependency, build, root-design, README, architecture, roadmap, requirements, compound, safety, minors/CSAM, or provider-bypass change would violate scope.

## Handoff

This design scopes one complete Phase 407 S1 status-sync slice. Executor updates only the allowed docs/test files, performs no staging/commit/push, does not create `acceptance.md`, and leaves parent/controller verification pending before any repository commit, push, or state finalization.
