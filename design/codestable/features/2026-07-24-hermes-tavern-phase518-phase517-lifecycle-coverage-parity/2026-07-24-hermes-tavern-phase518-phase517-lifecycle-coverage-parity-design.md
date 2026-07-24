---
doc_type: feature-design
feature: 2026-07-24-hermes-tavern-phase518-phase517-lifecycle-coverage-parity
status: approved
implementation_ready: true
bounded_phase: docs/static-test/lifecycle-hardening
parent_verification_status: pending_parent_verification
acceptance_state: pending_parent_verification
summary: Approved Phase 518 coverage parity for the accepted Phase 517 checklist lifecycle.
tags: [codestable, lifecycle, docs, static-test]
---

# Phase 518 Phase 517 Lifecycle Coverage Parity

## Scope

Add the accepted Phase 517 checklist to the focused CodeStable lifecycle static contract and advance the canonical attention current status to Phase 518. This phase changes no runtime, plugin, gateway, provider, or product behavior.

## Exact Contract

- `attention.md` advances to `All phases 1-518 accepted` and appends the Phase 518 label exactly once after Phase 517.
- The focused lifecycle test includes the Phase 517 checklist in its accepted-status coverage and preserves the existing Phase 511-516 requirements.
- The test's current-status assertions advance their ordered labels/range/suffix and stale guards without weakening historical protections.

## Constraints

Only attention, the focused status test, and this feature's design/checklist may change. Do not modify core Hermes files, plugin runtime, gateway, provider, auth, cron, Radar, README, architecture, root design, CI, or Phase 511-517 artifacts.

## Lifecycle

This slice has no acceptance artifact. During executor work the checklist remains non-final. The parent controller finalizes it only after independently rerunning every declared verification gate.

## Verification

- `python3 design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-24-hermes-tavern-phase518-phase517-lifecycle-coverage-parity`
- `python3 design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-24-hermes-tavern-phase518-phase517-lifecycle-coverage-parity/2026-07-24-hermes-tavern-phase518-phase517-lifecycle-coverage-parity-checklist.yaml --yaml-only`
- `python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`
