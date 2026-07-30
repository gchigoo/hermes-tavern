---
doc_type: feature-design
feature: 2026-07-30-hermes-tavern-phase526-phase525-acceptance-reference-integrity
requirement: docs
status: approved
implementation_ready: true
acceptance_state: pending
parent_verification_required: true
summary: Add an offline static contract tying the Phase 525 checklist acceptance reference to its existing acceptance artifact.
tags: [codestable, lifecycle, docs, static-test]
---

# Phase 526 Phase 525 Acceptance Reference Integrity

## Scope

Add focused static regressions that retain the existing Phase 525 checklist `acceptance_artifact` contract and lock the expected pending Phase 526 acceptance file and artifact identity. The regressions must compare exact repo-relative references, resolved files, matching frontmatter identities, gated attention progression through Phase 526, and Phase 527 absence.

## Boundaries

Only Phase 526 artifacts and the two focused static-test modules may change during S1. Phase 525 artifacts, runtime, plugin, core, auth, credential, provider, gateway, network, cron, Radar, CI, dependencies, README, architecture, root design, and product behavior are prohibited.

## Lifecycle

Executor implements S1 only. The Controller owns status promotion, attention progression, final verification, review, commit, and push. The Phase 526 acceptance artifact remains pending and non-final until controller gates pass.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest tests/test_hermes_tavern_design_docs.py tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`
