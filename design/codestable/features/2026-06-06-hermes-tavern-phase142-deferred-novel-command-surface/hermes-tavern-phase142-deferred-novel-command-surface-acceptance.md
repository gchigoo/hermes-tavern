---
doc_type: feature-acceptance
feature: "2026-06-06-hermes-tavern-phase142-deferred-novel-command-surface"
status: accepted
date: "2026-06-06"
summary: >
  Phase 142 is accepted as test-only command-surface regression hardening. It
  locks that deferred novel command families remain absent from the command
  table, generated help, and README Core commands while current archive/export
  commands remain visible, without making any deferred capability current.
tags: [novel, commands, deferred-boundary, regression, test-only, offline, acceptance]
---

# Phase 142 Deferred Novel Command Surface Acceptance

> Phase: S2 verify/accept test-only boundary
> Controller verification date: 2026-06-06
> Design: `design/codestable/features/2026-06-06-hermes-tavern-phase142-deferred-novel-command-surface/design.md`
> Checklist: `design/codestable/features/2026-06-06-hermes-tavern-phase142-deferred-novel-command-surface/checklist.yaml`

## 1. Scope and design contract

Phase 142 is accepted as regression hardening only. It introduces no user
command, command grammar, SQLite schema/table/index/migration, runtime API,
provider path, export format, prompt module, context-budget behavior,
retrieval/vectorization path, generation path, credential handling,
graph/alias/merge/split behavior, archive/importer behavior, media behavior,
safety behavior, architecture/root-design behavior, or Hermes core behavior.

Accepted S1 implementation surface:

- `tests/test_hermes_tavern_commands.py`
- `tests/test_hermes_tavern_readme_docs.py`

Accepted S2 status surface:

- this acceptance report
- `design/codestable/features/2026-06-06-hermes-tavern-phase142-deferred-novel-command-surface/checklist.yaml`

The feature remains intentionally test-only: deferred novel command families are
not implemented, routed, documented as current commands, or exposed through
public command surfaces.

## 2. S1 implementation evidence

S1 added paired absence and preservation guards in the two allowed test files:

- `tests/test_hermes_tavern_commands.py`
  - `test_help_omits_deferred_novel_command_literals` validates absence in generated help.
  - `test_tavern_command_table_omits_deferred_top_level_and_pseudo_families` validates top-level `TAVERN_COMMAND_TABLE` omissions.
  - `test_tavern_command_table_keeps_current_allowed_top_level_families` validates preserved current command families.
  - `test_help_keeps_current_allowed_command_literals` validates help-surface command preservation.
- `tests/test_hermes_tavern_readme_docs.py`
  - `test_readme_core_commands_omit_deferred_novel_command_literals` validates absence in README Core commands.
  - `test_readme_core_commands_keeps_current_allowed_command_literals` validates preserved current commands in README.

Both test files use segment-aware command matching so command syntax containing
Markdown pipes, especially `/rp export [markdown|st-json]`, does not create false
matches while checking deferred literals.

## 3. Deferred command absence matrix

Controller acceptance confirms that the test matrix covers the deferred command
families named by the design:

| Category | Deferred command literals |
|---|---|
| Archive/import/zip | `/rp project archive`, `/rp project import`, `/rp project zip`, `/rp novel import`, `/rp novel archive` |
| Outline generation | `/rp project outline generate`, `/rp project outline rewrite`, `/rp project outline expand`, `/rp project outline compress`, `/rp outline generate`, `/rp outline rewrite`, `/rp outline expand`, `/rp outline compress` |
| Canon automation | `/rp canon check`, `/rp canon conflict`, `/rp canon pin` |
| Relationship automation | `/rp relationship graph`, `/rp relationship alias`, `/rp relationship merge`, `/rp relationship split`, `/rp relationship extract` |
| Location automation | `/rp location map`, `/rp location geocode`, `/rp location coordinates` |
| Volume/arc | `/rp project volume`, `/rp project arc`, `/rp volume`, `/rp arc` |

The command-table guard also covers deferred top-level and pseudo-family names:
`novel`, `volume`, `arc`, `outline`, `project-import`, `project-archive`,
`canon-check`, `canon-conflict`, `canon-pin`, `relationship-graph`,
`relationship-alias`, `relationship-merge`, `relationship-split`, and `geocode`.

## 4. Current allowed command preservation

The same regression surface preserves current archive/export commands instead of
blocking nearby legitimate command names:

- `/rp project export [id]`
- `/rp export [markdown|st-json]`
- `/rp archive`

This is important because naive substring checks for `/rp arc` or pipe-separated
Markdown rows could otherwise break legitimate existing UX.

## 5. Reverse-scope and no-behavior-change boundaries

Controller review confirms S2 changed only CodeStable status/acceptance files.
S1 implementation remains limited to the two approved test files from the prior
commit. There are no current diffs to:

- `README.md`
- `src/**`
- `tests/**` during S2
- `run_agent.py`
- `cli.py`
- `gateway/run.py`
- `plugins/**`
- `build/lib/**`
- `design/HERMES_TAVERN_DESIGN.md`
- `design/codestable/architecture/ARCHITECTURE.md`

No source, runtime, provider, generation, credential, importer/exporter, archive
pipeline, graph/alias/merge/split/extract, geocode/map, volume/arc, safety, or
Hermes core behavior changed during acceptance.

## 6. Architecture and root-design writeback

No architecture or root-design writeback is required.

Design §4 explicitly states that Phase 142 does not make any deferred root-design
capability current. This acceptance pass confirms that conclusion: the phase only
adds regression tests that keep deferred command families absent. Updating
architecture or `design/HERMES_TAVERN_DESIGN.md` would incorrectly imply a new
current capability.

## 7. Requirement and roadmap writeback

No requirement or roadmap writeback is required.

The design frontmatter declares no `requirement`, `roadmap`, or `roadmap_item`.
The feature is a regression-hardening action rather than a new user-facing
capability, so there is no requirement document to promote and no roadmap item to
mark done.

## 8. Verification ledger

Controller reran the verification commands after the executor drafted the S2
acceptance artifact:

| Command | Result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py` | passed; no output |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` | passed; 84 passed in 0.10s |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` | passed; 1021 passed in 52.13s |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` | passed; 1021 passed in 49.24s |
| `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase142-deferred-novel-command-surface/design.md --require doc_type --require status --require feature` | passed |
| `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase142-deferred-novel-command-surface/hermes-tavern-phase142-deferred-novel-command-surface-acceptance.md --require doc_type --require status --require feature` | passed |
| `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-06-hermes-tavern-phase142-deferred-novel-command-surface/checklist.yaml` | passed |
| `git diff --name-only -- README.md src tests run_agent.py cli.py gateway/run.py plugins build/lib design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md` | passed; empty output |
| `git diff --check` | passed; no output |

Executor JSONL note: the executor had one harmless failed pre-create read of the
acceptance file before writing it. The final file exists and controller validators
passed.

## 9. Attention candidates

No `attention.md` update is needed. This phase did not expose a new recurring
workflow, environment, command, or project constraint; it followed the existing
CodeStable test-only acceptance pattern.

## 10. Residual and deferred work

Deferred novel capabilities remain intentionally unimplemented until future
features design their product, routing, schema, export, provider, and safety
contracts explicitly. This accepted phase only prevents accidental public command
surface exposure of those unresolved capabilities.
