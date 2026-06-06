---
doc_type: feature-design
feature: "2026-06-06-hermes-tavern-phase142-deferred-novel-command-surface"
status: approved
date: "2026-06-06"
summary: >
  Add test-only command-surface regressions proving currently deferred novel
  command families remain absent from the Tavern command table, generated help,
  and README Core commands. No source, docs, runtime, provider, generation,
  credential, importer/exporter, architecture, or product behavior changes are
  in scope.
tags: [novel, commands, deferred-boundary, regression, test-only, offline]
---

# Phase 142: Deferred Novel Command Surface Regression

## 0. Terms

| Term | Meaning | Conflict guard |
|---|---|---|
| Deferred Novel Command Surface | Command literals from the root design that are intentionally not current Hermes Tavern behavior. | Not current `/rp project export [id]`, `/rp export`, or session `/rp archive`. |
| Absence Matrix | Tests that assert deferred command literals are absent from public command surfaces. | Not a runtime command implementation and not a product decision. |
| Public Command Surface | `TAVERN_COMMAND_TABLE` help lines, generated `/rp help` text, and README Core commands. | Not design docs; design docs intentionally mention deferred future ideas. |

## 1. Decisions And Constraints

Need:

The recent accepted phases made many metadata families current while repeatedly preserving deferred boundaries for archive/import, canon check/conflict/pin, outline generation/rewrite/expand/compress, relationship graph/aliases/merge-split/automatic extraction, location map/geocode derivatives, and volume/arc. A test-only absence matrix is the smallest safe next slice because it locks that boundary without choosing schemas, routing, export formats, provider behavior, or generation semantics.

Success:

- Tests define one explicit deferred novel command literal list.
- Generated help omits every deferred literal.
- README Core commands omit every deferred literal.
- The top-level command table omits deferred top-level families and pseudo-families.
- Current allowed commands remain allowed, especially `/rp project export [id]`, `/rp export [markdown|st-json]`, and session `/rp archive`.
- S1 changes tests only.

Hard constraints:

- No source changes.
- No README/docs edits.
- No CodeStable acceptance/status/writeback changes during S1.
- No provider/network calls, generation calls, credential handling, safety bypass, minors/underage paths, graph behavior, aliases, merge/split, automatic extraction, vectorization, retrieval, summarization, archive import/export, ST importer/exporter, or SillyTavern asset compatibility changes.
- Never edit `run_agent.py`, `cli.py`, `gateway/run.py`, `src/hermes_tavern/runtime.py`, `plugins/**`, or `build/lib/**`.

## 2. Names And Flow

### 2.1 Noun Layer

Current:

- `tests/test_hermes_tavern_commands.py` already verifies generated help is built from `TAVERN_COMMAND_TABLE` and contains current command literals.
- `tests/test_hermes_tavern_readme_docs.py` already verifies README Core commands cover current command families.
- `tests/test_hermes_tavern_commands.py` has a small guard against top-level `revision` and `relationship-rename` families.
- Root design still explicitly defers several novel command groups.

Change:

Add a test-owned deferred literal list covering at minimum:

- `/rp project archive`
- `/rp project import`
- `/rp project zip`
- `/rp novel import`
- `/rp novel archive`
- `/rp project outline generate`
- `/rp project outline rewrite`
- `/rp project outline expand`
- `/rp project outline compress`
- `/rp outline generate`
- `/rp outline rewrite`
- `/rp outline expand`
- `/rp outline compress`
- `/rp canon check`
- `/rp canon conflict`
- `/rp canon pin`
- `/rp relationship graph`
- `/rp relationship alias`
- `/rp relationship merge`
- `/rp relationship split`
- `/rp relationship extract`
- `/rp location map`
- `/rp location geocode`
- `/rp location coordinates`
- `/rp project volume`
- `/rp project arc`
- `/rp volume`
- `/rp arc`

Top-level table guard should include deferred pseudo-families such as `novel`, `volume`, `arc`, `outline`, `project-import`, `project-archive`, `canon-check`, `canon-conflict`, `canon-pin`, `relationship-graph`, `relationship-alias`, `relationship-merge`, `relationship-split`, and `geocode`.

### 2.2 Orchestration Layer

S1 flow:

```text
tests only
  -> read generated help from _build_help_text()
  -> assert every deferred literal is absent
  -> read README Core commands section
  -> assert every deferred literal is absent
  -> assert deferred top-level command names are absent from TAVERN_COMMAND_TABLE
  -> assert current allowed commands still remain visible
```

Flow constraints:

- Do not dispatch runtime commands.
- Do not add placeholder handlers.
- Do not edit command tables, README, source, architecture, or root design.
- Do not grep design docs for absence, because design docs intentionally record deferred future work.

### 2.3 Mount Points

Allowed S1 files:

| File | Purpose |
|---|---|
| `tests/test_hermes_tavern_commands.py` | Add generated-help and top-level table absence regressions. |
| `tests/test_hermes_tavern_readme_docs.py` | Add README Core command absence regression. |

Prohibited S1 files:

- `src/**`
- `README.md`
- `docs/**`
- `design/HERMES_TAVERN_DESIGN.md`
- `design/codestable/**`
- `run_agent.py`
- `cli.py`
- `gateway/**`
- `plugins/**`
- `build/lib/**`
- `tests/test_hermes_tavern_novel_db.py`
- `tests/test_hermes_tavern_novel_runtime.py`

### 2.4 Slicing

S1 only: add the test-only deferred command surface regressions.

S2: controller-owned verification and acceptance artifact after S1 passes. No architecture or root-design writeback is expected because this phase changes no behavior.

### 2.5 Structure Health

No pre-feature micro-refactor.

The two target test files already own command-table/help and README command-surface assertions. Adding small absence tests there is lower risk than creating a new test module or touching runtime source.

## 3. Acceptance Criteria

1. S1 changes only `tests/test_hermes_tavern_commands.py` and `tests/test_hermes_tavern_readme_docs.py`.
2. Generated help omits all deferred novel command literals listed in this design.
3. README Core commands omit all deferred novel command literals listed in this design.
4. `TAVERN_COMMAND_TABLE` omits deferred top-level families and pseudo-families.
5. Tests explicitly preserve current allowed commands: `/rp project export [id]`, `/rp export [markdown|st-json]`, and `/rp archive`.
6. No runtime route, command handler, command table entry, README text, source behavior, architecture/root design, provider/generation path, credential path, importer/exporter behavior, archive workflow, graph/alias/merge/split/extraction behavior, geocode/map behavior, volume/arc behavior, or safety behavior changes.
7. Focused and Tavern-wide pytest commands pass offline.
8. CodeStable design/checklist validators pass after controller materializes the artifact.
9. Reverse-scope checks show no prohibited paths changed.

## 4. Architecture/Root Design Relationship

This phase does not make any deferred root-design capability current. It reinforces the current architecture boundary by proving deferred novel command families are not exposed through public command surfaces. No architecture or root-design writeback is required until a later approved feature intentionally implements one of those deferred capabilities.
