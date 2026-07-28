---
doc_type: feature-design
feature: 2026-07-27-hermes-tavern-phase520-canonical-design-plan-path-parity
status: approved
implementation_ready: true
bounded_phase: docs/static-test/canonical-path-parity
parent_verification_status: completed
acceptance_state: accepted
summary: Plan the canonical design and implementation-plan path parity correction without creating a second plan authority.
tags: [codestable, docs, static-test, canonical-path]
---

# Phase 520 Canonical Design-Plan Path Parity

## Scope

This planning-only phase records a narrow later implementation slice to correct stale references to the tracked implementation plan. The canonical documents are `design/HERMES_TAVERN_DESIGN.md` and `design/plans/hermes-tavern-implementation-v0.1.md`. No second plan file, symlink, or `.hermes/plans/` mirror may be created.

## Contract

The later implementation must update only the five known stale path references: root design section 23, the attention entry, the implementation plan Read First reference and self-reference, and the active credential-reuse decision reference. A focused static test must prove both canonical paths exist, the obsolete `.hermes/plans/hermes-tavern-implementation-v0.1.md` path remains absent, and the four current authority documents no longer contain that obsolete plan path.

After the path contract passes, the later slice records Phase 520 as pending independent controller verification while retaining accepted history through Phase 519 only. It must exclude Phase 521, preserve ordering/uniqueness guards, and leave the adult-fiction safety boundary in root design section 12.3 unchanged.

## Boundaries

The planned implementation allowlist is `design/HERMES_TAVERN_DESIGN.md`, `design/plans/hermes-tavern-implementation-v0.1.md`, `design/codestable/attention.md`, `design/codestable/compound/2026-05-18-decision-hermes-tavern-credential-reuse.md`, `tests/test_hermes_tavern_design_docs.py`, `tests/test_hermes_tavern_codestable_status.py`, and this feature directory. Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `src/**`, `plugins/**`, `gateway/**`, `.hermes/**`, README, CI, dependencies, auth, provider, credentials, network, cron, command behavior, import/export behavior, model behavior, or historical Phase 1–519 artifacts.

## Lifecycle

Controller verification completed the declared YAML, compile, focused, full-suite, scope, and whitespace gates. The company-policy final Architect review returned PASS, so the lifecycle is accepted; the acceptance artifact records the controller evidence.

## Verification

- `python3 design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-27-hermes-tavern-phase520-canonical-design-plan-path-parity`
- `python3 design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-27-hermes-tavern-phase520-canonical-design-plan-path-parity/2026-07-27-hermes-tavern-phase520-canonical-design-plan-path-parity-checklist.yaml --yaml-only`
- `python -m py_compile tests/test_hermes_tavern_design_docs.py tests/test_hermes_tavern_codestable_status.py`
- `python -m pytest tests/test_hermes_tavern_design_docs.py tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`
