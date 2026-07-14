---
doc_type: feature-acceptance
feature: 2026-07-14-hermes-tavern-phase488-codestable-verification-command-parity
status: accepted
accepted_at: 2026-07-14
summary: Aligned the mandatory Tavern CodeStable verification commands with the repository layout and protected them with a regression test.
tags: [hermes-tavern, codestable, verification, regression, phase488]
---

## Scope and behavior

The active `attention.md` test section now names the existing Tavern test glob, the canonical full suite, and the existing card-fixture directory. The status fixture locks all three literals, rejects obsolete `tests/plugins/` and `scripts/run_tests.sh` references, and preserves the existing Phase 1-487 status contract.

## Boundaries

No plugin/runtime/product behavior changed. No gateway, provider, prompt, credential, database, CI workflow, package, README, or script file changed.

## Controller verification

- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-14-hermes-tavern-phase488-codestable-verification-command-parity/design.md --require doc_type --require status` — passed.
- `python -m py_compile tests/test_hermes_tavern_codestable_status.py` — passed.
- `python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider` — passed: 2 tests.
- `python -m pytest -q -o 'addopts=' -p no:cacheprovider` — passed: 1216 tests.
- exact changed-path guard and `git diff --check` — passed before lifecycle writeback; rerun after writeback is required before commit.
