---
doc_type: feature-design
feature: 2026-07-01-hermes-tavern-phase406-attention-status-sync-through-phase405
title: "Phase 406 attention/status sync through Phase 405"
status: approved
implementation_ready: true
date: "2026-07-01"
owner: company_boost_lane
lane: company-boost/uncommitted
bounded_phase: "docs/static-test/status-only"
summary: "Approved design for Phase 406 attention/status sync through accepted Phase 405; S1 worker handoff only, pending parent verification, with no executor commit or push."
parent_verification_status: pending_parent_verification
acceptance_state: pending_parent_verification
parent_verification_required: true
worker_commit_or_push_performed: false
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase406, company-boost]
---

# Phase 406 attention/status sync through Phase 405

## Background / Current Status Evidence

Phase 405 is already accepted and complete. The current CodeStable attention status line is synced through `All phases 1-405 accepted`, Phase 405 artifacts are present and accepted, Phase 404 artifacts are accepted, the focused status regression is pinned to the Phase 405 contract, and no Phase 406 feature directory existed before the read-only architect pass.

Therefore Phase 406 is the next safe bounded CodeStable slice.

## Goals

- Materialize the Phase 406 design/checklist artifact set for an S1 company-boost dirty-tree handoff.
- Advance `design/codestable/attention.md` exactly one status tick from 1-405 to 1-406.
- Append `Phase 406 attention status sync through Phase 405` exactly once in the attention current-status line.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 405 label.
- Update the focused status regression to guard the Phase 406 live status contract.
- Record truthful S1 worker evidence while leaving parent/controller verification pending; executor does not stage, commit, or push.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency changes.
- No root-design, README, architecture, roadmap, requirements, compound, review, build, or cache changes.
- No acceptance.md creation during S1.
- No broad rewrites, refactors, dependency installs, network calls, service starts, staging, commits, or pushes.
- No Hermes-native plugin architecture or SillyTavern asset compatibility changes.
- No provider-safety bypass, adult-fiction policy change, RP compatibility change, minors-related work, or CSAM-related work.
- No parent/controller verification completion inside this executor slice.
- No Phase 407 or later work.

## Allowed Files

Only these files are in scope:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-01-hermes-tavern-phase406-attention-status-sync-through-phase405/design.md`
- `design/codestable/features/2026-07-01-hermes-tavern-phase406-attention-status-sync-through-phase405/checklist.yaml`

## Exact Status Contract

### attention.md

- Current prefix advances from `Current status (2026-06-18): All phases 1-405 accepted` to `Current status (2026-06-18): All phases 1-406 accepted`.
- Append exactly once in the attention status line: `Phase 406 attention status sync through Phase 405`.
- Preserve `Phase 121-167` and every explicit Phase 168 through Phase 405 label.
- Preserve the status line placement under `### 其他`, immediately after the adult-fiction boundary bullet and before `### Hermes Tavern 凭证约束`.
- Final suffix becomes exactly: `Phase 404 attention status sync through Phase 403, Phase 405 attention status sync through Phase 404, and Phase 406 attention status sync through Phase 405.`

### tests/test_hermes_tavern_codestable_status.py

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-406 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-405 accepted"`
- `STALE_PHASE_MARKER = "1-405"`
- `STALE_PHASE_MARKER_EN_DASH = "1–405"`
- Append `"Phase 406 attention status sync through Phase 405"` to `REQUIRED_PHASE_LABELS`.
- Preserve every existing Phase 168 through Phase 405 required label.
- `FINAL_STATUS_SUFFIX = "Phase 404 attention status sync through Phase 403, Phase 405 attention status sync through Phase 404, and Phase 406 attention status sync through Phase 405."`
- `phase_range = range(168, 407)`
- `aggregate_range = "range(168, 407)"`
- Add `stale_aggregate_range_406 = "".join(["range(168, ", "40", "6", ")"])`.
- Include `stale_aggregate_range_406` in the stale assertion tuple.
- Preserve prior split stale guards, including `stale_aggregate_range_405`, `stale_aggregate_range_404`, `stale_aggregate_range_403`, and earlier.
- Replace the final split `stale_aggregate_guard` so it builds stale `range(168, 406)` without embedding contiguous `range(168, 406)` in the test source.
- Do not leave a contiguous stale literal `range(168, 406)` in the focused test source after the update; the live range is `range(168, 407)`.
- Preserve anchored assignment-count guards for `CURRENT_STATUS_PREFIX` and `FINAL_STATUS_SUFFIX`; do not replace them with naive substring counts.
- Preserve the in-test section-placement assertion for the current-status bullet.
- Preserve split no-discovery-token guards against `.glob`, `.rglob`, `iterdir`, and `os.walk`.
- Newest-label exact-once applies to the attention status line only. Do not require exact once across the test source because the newest label appears in `REQUIRED_PHASE_LABELS` and `FINAL_STATUS_SUFFIX`.

## Static Guard Requirements

Parent/controller verification must reject the implementation unless all changed/untracked paths are exactly the four allowed Phase 406 paths listed above and no runtime/source/plugin/provider/gateway/CLI/config/dependency/root-design/README/architecture/roadmap/requirements/compound/review/build/cache path changed.

Static checks must verify the exact current-status prefix, stale prefix, stale hyphen/en-dash markers, final suffix, preservation of `Phase 121-167`, preservation of every explicit Phase 168 through Phase 405 label, append of Phase 406 exactly once in the attention status line, current-status section placement, anchored assignment-count guards, no direct stale `range(168, 406)` literal in the focused test source, no discovery tokens, no Phase 406 acceptance.md in S1, final newlines, and no trailing whitespace.

## Structure Health / Microrefactor Decision

No microrefactor is part of this slice. The only planned work is a bounded status-line update, a focused static regression update, and creation of the selected Phase 406 feature design/checklist artifacts. Changing runtime structure, plugin/provider boundaries, root design, architecture, roadmap, requirements, compound documents, or acceptance artifacts would be outside scope.

## Verification Commands

Worker-side execution in S1 may run the YAML validators, compile check, focused status pytest, static guard, and `git diff --check`; parent/controller verification remains pending after this executor handoff and is responsible for full-suite verification and final acceptance decisions.

Recommended worker/controller gates:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-01-hermes-tavern-phase406-attention-status-sync-through-phase405 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase406 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static allowed-path/status/scope/final-newline/trailing-whitespace guard over `git diff --name-only` plus `git ls-files --others --exclude-standard`.
- `git diff --check`

## Risks

- The long `attention.md` status line is easy to damage by dropping a prior explicit phase label.
- The terminal `and` must move to Phase 406; Phase 405 should become comma-separated.
- `range(168, 406)` becomes stale and must not remain as a contiguous stale literal in the focused test source.
- Existing split stale guards, especially `stale_aggregate_range_405`, must remain present in the stale tuple.
- Newest-label exact-once applies only to the attention status line, not to the whole test source.
- Any runtime, provider, gateway, CLI, config, dependency, build, root-design, README, architecture, roadmap, requirements, compound, safety, minors/CSAM, or provider-bypass change would violate scope.

## Handoff

This design scopes one complete Phase 406 S1 status-sync slice. Executor updates only the allowed docs/test files, performs no staging/commit/push, does not create `acceptance.md`, and leaves parent/controller verification pending before any repository commit, push, or state finalization.
