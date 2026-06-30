---
doc_type: feature-acceptance
feature: 2026-07-01-hermes-tavern-phase396-attention-status-sync-through-phase395
status: accepted
accepted_at: "2026-07-01"
owner: standard_lane
lane: standard/personal
bounded_phase: "docs/static-test/status-only"
summary: "Phase 396 attention/status sync through Phase 395 accepted after parent verification."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase396, standard-lane]
---

# Phase 396 attention/status sync acceptance

## Result

Accepted. Phase 396 advances the CodeStable startup attention status from all phases 1-395 accepted to all phases 1-396 accepted and appends `Phase 396 attention status sync through Phase 395` while preserving the historical Phase 121-167 aggregate and every explicit Phase 168 through Phase 395 label.

## Scope

This was a docs/static-test/status-only slice. Changed files are limited to:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-01-hermes-tavern-phase396-attention-status-sync-through-phase395/design.md`
- `design/codestable/features/2026-07-01-hermes-tavern-phase396-attention-status-sync-through-phase395/checklist.yaml`
- `design/codestable/features/2026-07-01-hermes-tavern-phase396-attention-status-sync-through-phase395/acceptance.md`

No runtime/source/plugin/provider/gateway/CLI/config/dependency/root-design/README/architecture/roadmap/requirements/compound/build/cache files changed. Hermes-native plugin architecture and SillyTavern asset compatibility remain unchanged. No provider-safety bypass, minors/CSAM behavior, credentials, or service lifecycle work was introduced.

## Codex Artifacts

- Architect design pass: `/tmp/hermes-tavern-architect-phase396-20260701-0658.jsonl`
- Executor S1 pass: `/tmp/hermes-tavern-executor-phase396-20260701-0703.jsonl`
- Architect S1 review: `/tmp/hermes-tavern-architect-review-phase396-20260701-0722.jsonl`

The first architect review requested a checklist-only S1 status reconciliation. The parent/controller applied that mechanical checklist update, reran the relevant validators and guards, and the second read-only architect review returned `REVIEW_RESULT: PASS`.

## Controller Verification

Parent/controller reran and passed:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase396-attention-status-sync-through-phase395/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase396-attention-status-sync-through-phase395/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static Phase 396 status/scope/final-newline/trailing-whitespace guard over changed and untracked files
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` (1215 passed)
- `git diff --check`

## Status Contract

The accepted status line now starts with `Current status (2026-06-18): All phases 1-396 accepted`, includes `Phase 396 attention status sync through Phase 395` exactly once, and ends with `Phase 394 attention status sync through Phase 393, Phase 395 attention status sync through Phase 394, and Phase 396 attention status sync through Phase 395.`

The focused status regression now guards the Phase 396 contract, including the Phase 396 current prefix, Phase 395 stale markers, `range(168, 397)` live aggregate, split stale `range(168, 396)` guard, anchored assignment-count checks, section placement, and no-discovery-token protections.
