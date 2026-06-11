---
doc_type: feature-acceptance
status: accepted
feature: "2026-06-11-hermes-tavern-phase170-export-surface-regression"
date: "2026-06-11"
summary: "Phase 170 test-only export command-surface regression coverage is implemented, verified, and accepted."
owner: codestable-cron
---

# Phase 170 Acceptance: Export Command-Surface Regression

## Scope

Phase 170 adds test-only regression coverage for implemented export command literals
in generated `/rp help` output and README Core command documentation sections.
It is strictly bounded to regression assertions in tests and does not change
runtime handlers, command behavior, docs text, schemas, payloads, or plugin/runtime
surfaces.

No root-design or architecture writeback is required because this is test-only and
introduced no new runtime/docs command behavior.

## Codex Two-Stage Evidence

- Architect pass: `/tmp/hermes-tavern-architect-phase170-s2.jsonl`
  - Decision: `RESULT: PHASE170_S2_ACCEPTANCE_ARTIFACT; READY.`
  - Scope confirmed: S2 acceptance artifacts only.
- Executor pass: `/tmp/hermes-tavern-executor-phase170-s2.jsonl`
  - Drafted S2 in the approved files only, leaving final accepted/completed/passed
    status to the controller.
- Controller: reran validators, focused tests, full pytest, protected-path guards,
  and git diff whitespace checks before finalizing accepted status.

## Implementation Summary

Created:

- `design/codestable/features/2026-06-11-hermes-tavern-phase170-export-surface-regression/phase170-acceptance.md`
  - Added frontmatter with `status: accepted` after controller verification.
  - Added sections: Scope, Codex Two-Stage Evidence, Implementation Summary,
    Verification Summary, Controller-Run Commands, Acceptance Checks,
    Residual Risk / Next Step.
- `design/codestable/features/2026-06-11-hermes-tavern-phase170-export-surface-regression/checklist.yaml`
  - Set root `status: accepted`.
  - Preserved C1–C4 as `passed` with prior controller evidence.
  - Added S2 and finalized it as `completed` after controller verification.
  - Added C5 acceptance-frontmatter check and marked it `passed` after validation.

No additional file changes were made outside the approved set.

## Verification Summary

| Item | Result |
| --- | --- |
| C1 | PASSED: targeted command/readme tests |
| C2 | PASSED: no protected/runtime files changed |
| C3 | PASSED: full pytest suite |
| C4 | PASSED: diff whitespace check |
| C5 | PASSED: acceptance frontmatter validation |
| Controller final validators | PASSED: design, checklist, and acceptance required frontmatter/fields valid |
| Controller py_compile | PASSED |
| Controller targeted command/readme tests | PASSED — 105 passed |
| Controller full pytest suite | PASSED — 1204 passed |
| Protected-path guard | PASSED — no runtime/source/README/root-design/architecture/plugin/build paths changed |
| `git diff --check` | PASSED |

## Controller-Run Commands

```bash
python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-11-hermes-tavern-phase170-export-surface-regression/design.md --require doc_type --require status --require feature
python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-11-hermes-tavern-phase170-export-surface-regression/checklist.yaml --yaml-only --require doc_type --require status --require feature
python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-11-hermes-tavern-phase170-export-surface-regression/phase170-acceptance.md --require doc_type --require status --require feature
PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider
git diff --name-only -- run_agent.py cli.py gateway/run.py src README.md design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md plugins build/lib
git status --short -- run_agent.py cli.py gateway/run.py src README.md design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md plugins build/lib
git diff --check
```

## Acceptance Checks

- Command-surface regression scope: PASS (added for generated help and README Core commands only).
- Behavior preservation: PASS (no runtime/runtime docs behavior or payload changes).
- Root-design/architecture writeback required: PASS, not required for this test-only slice.
- Checklist integrity: PASS (root accepted, S2 completed, C5 passed after controller validation).

## Residual Risk / Next Step

No residual functional risk from this slice. Phase 170 is closed; a future tick can
select the next bounded command-surface/doc parity or local metadata/export
hardening gap via a fresh architect pass.
