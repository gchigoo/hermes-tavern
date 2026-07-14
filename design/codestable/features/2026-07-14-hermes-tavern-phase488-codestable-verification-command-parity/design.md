---
doc_type: feature-design
feature: 2026-07-14-hermes-tavern-phase488-codestable-verification-command-parity
status: approved
requirement: ci-quality
summary: Keep mandatory Tavern CodeStable verification commands aligned with the repository test layout.
tags: [hermes-tavern, codestable, verification, docs, regression]
---

## Goal

Correct stale mandatory verification instructions in `design/codestable/attention.md` and lock them with the existing CodeStable status test.

## Scope

Update only the attention test-command bullets and add a static regression assertion. The canonical focused command is `python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`; the full-suite command is `python -m pytest -q -o 'addopts=' -p no:cacheprovider`; card fixtures are under `tests/fixtures/cards/`.

## Boundaries

No runtime, plugin, gateway, provider, prompt, credential, database, README, CI workflow, package, or script changes. Do not alter the current Phase 1-487 status line or its labels. Do not create a `scripts/run_tests.sh` compatibility wrapper.

## Acceptance

The focused status test must prove the current instructions are exact, stale paths are absent, and the fixture directory exists. Controller verification runs YAML validation, `py_compile`, focused status test, full pytest, and whitespace/scope guards.
