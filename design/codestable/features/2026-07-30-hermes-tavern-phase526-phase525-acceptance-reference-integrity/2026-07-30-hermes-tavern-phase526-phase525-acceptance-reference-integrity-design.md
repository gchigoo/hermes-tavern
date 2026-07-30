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

Add one focused static regression for the existing Phase 525 checklist `acceptance_artifact` reference and create the Phase 526 design/checklist. The regression must compare the exact repo-relative reference, resolved file, and acceptance frontmatter identity.

## Boundaries

Only Phase 526 artifacts and the two focused static-test modules may change during S1. Phase 525 artifacts, runtime, plugin, core, auth, credential, provider, gateway, network, cron, Radar, CI, dependencies, README, architecture, root design, and product behavior are prohibited.

## Lifecycle

Executor implements S1 only. The Controller owns acceptance creation, status promotion, attention progression, final verification, review, commit, and push. No Phase 526 acceptance artifact exists before controller gates pass.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest tests/test_hermes_tavern_design_docs.py tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`