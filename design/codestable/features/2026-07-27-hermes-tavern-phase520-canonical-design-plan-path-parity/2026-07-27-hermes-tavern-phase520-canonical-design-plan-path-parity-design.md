---
doc_type: feature-design
feature: 2026-07-27-hermes-tavern-phase520-canonical-design-plan-path-parity
status: draft
implementation_ready: false
bounded_phase: docs/static-test/canonical-path-parity
parent_verification_status: pending
acceptance_state: not_started
summary: Plan the canonical design and implementation-plan path parity correction without creating a second plan authority.
tags: [codestable, docs, static-test, canonical-path]
---

# Phase 520 Canonical Design-Plan Path Parity

## Scope

This planning-only phase records a narrow later implementation slice to correct stale references to the tracked implementation plan. The canonical documents are `design/HERMES_TAVERN_DESIGN.md` and `design/plans/hermes-tavern-implementation-v0.1.md`. No second plan file, symlink, or `.hermes/plans/` mirror may be created.

## Contract

The later implementation must update only the four known stale path references: root design section 23, the attention entry, the implementation plan Read First reference, and its self-reference. A focused static test must prove both canonical paths exist, the obsolete `.hermes/plans/hermes-tavern-implementation-v0.1.md` path remains absent, and the three current authority documents no longer contain that obsolete plan path.

After the path contract passes, the later slice may advance canonical attention/status evidence through Phase 520 only. It must retain Phase 1–519 history, exclude Phase 521, preserve ordering/uniqueness guards, and leave the adult-fiction safety boundary in root design section 12.3 unchanged.

## Boundaries

The planned implementation allowlist is `design/HERMES_TAVERN_DESIGN.md`, `design/plans/hermes-tavern-implementation-v0.1.md`, `design/codestable/attention.md`, `tests/test_hermes_tavern_design_docs.py`, `tests/test_hermes_tavern_codestable_status.py`, and this feature directory. Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `src/**`, `plugins/**`, `gateway/**`, `.hermes/**`, README, CI, dependencies, auth, provider, credentials, network, cron, command behavior, import/export behavior, model behavior, or historical Phase 1–519 artifacts.

## Lifecycle

This is a draft planning artifact. No implementation, acceptance artifact, lifecycle promotion, or Phase 520 status advance has occurred. The controller must obtain a fresh implementation-stage architecture validation before any executor work.

## Verification

- `python3 design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-27-hermes-tavern-phase520-canonical-design-plan-path-parity`
- `python3 design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-27-hermes-tavern-phase520-canonical-design-plan-path-parity/2026-07-27-hermes-tavern-phase520-canonical-design-plan-path-parity-checklist.yaml --yaml-only`
- `python -m py_compile tests/test_hermes_tavern_design_docs.py tests/test_hermes_tavern_codestable_status.py`
- `python -m pytest tests/test_hermes_tavern_design_docs.py tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`
