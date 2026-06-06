---
doc_type: feature-acceptance
feature: "2026-06-06-hermes-tavern-phase143-canon-inspect-surface"
status: accepted
date: "2026-06-06"
summary: >
  Phase 143 is accepted as a bounded read-only canon inspect surface. The
  current `/rp canon inspect <canon-id>` command exposes one existing
  `novel_canon` row for command-visible inspection while preserving canon
  prompt behavior and keeping canon check/conflict/pin, correlation,
  retrieval/vectorization, provider, generation, archive/import, credential,
  and safety behavior deferred.
tags: [hermes-tavern, canon, command-surface, offline, acceptance]
---

# Phase 143 Canon Inspect Surface Acceptance

> Phase: S2 verify/accept docs/status closeout
> Controller verification date: 2026-06-06
> Design: `design/codestable/features/2026-06-06-hermes-tavern-phase143-canon-inspect-surface/design.md`
> Checklist: `design/codestable/features/2026-06-06-hermes-tavern-phase143-canon-inspect-surface/checklist.yaml`

## 1. Scope and S1 contract

Phase 143 accepts the S1 implementation of a single read-only command surface:
`/rp canon inspect <canon-id>`. The feature stays under the existing `canon`
command family and uses existing `novel_canon` storage.

Accepted S1 implementation surface:

- `src/hermes_tavern/db_novel.py`
- `src/hermes_tavern/runtime_novel.py`
- `src/hermes_tavern/commands.py`
- `README.md`
- `tests/test_hermes_tavern_novel_db.py`
- `tests/test_hermes_tavern_novel_runtime.py`
- `tests/test_hermes_tavern_commands.py`
- `tests/test_hermes_tavern_readme_docs.py`

Accepted S2 docs/status/writeback surface:

- this acceptance report
- `design/codestable/features/2026-06-06-hermes-tavern-phase143-canon-inspect-surface/checklist.yaml`
- `design/codestable/architecture/ARCHITECTURE.md`
- `design/HERMES_TAVERN_DESIGN.md`

No source, runtime, README, or test files changed during S2.

## 2. Store/interface contract

Controller review confirms the S1 store/interface contract matches the design:

- `TavernStore.get_canon(canon_id)` is a read-only helper returning one
  `novel_canon` row or `None`.
- The helper does not create a table, migration, index, ordering change, prompt
  selector, export path, provider route, model route, credential path, or
  generation behavior.
- Existing `list_canon` and `get_canon_for_prompt` ordering remain covered by
  regression tests.

## 3. Command/help/README behavior contract

Controller verification confirms current command visibility and bounded command
behavior:

- `/rp canon inspect <canon-id>` is visible in generated `/rp help` and README
  Core commands.
- A valid id returns bounded row details: id, project id, title, canon group,
  and a mobile content preview.
- Missing, malformed, or extra arguments return bounded usage or not-found
  messages.
- The route remains nested under the existing `canon` family; no new top-level
  command family or `runtime.py` shim was added.

## 4. Deferred/no-leak boundary

Phase 143 does **not** implement deferred canon analysis or automation:

- `/rp canon check`
- `/rp canon conflict`
- `/rp canon pin <fact>`
- canon correlation/graph/extraction tooling
- retrieval/vectorization coupling
- provider/model routing or generation side effects
- archive/import/ZIP workflows
- credential handling
- safety-policy behavior

Reverse-scope guards confirmed no `canon inspect`/`get_canon` references landed
in prompt assembly, debug/context-budget, provider/model, generation, runtime
content, adapter, or importer paths.

## 5. Architecture and root-design writeback

S2 intentionally updates project-level current-state docs because `/rp canon
inspect <canon-id>` is now a current user-facing command surface:

- `ARCHITECTURE.md`
  - advances `/rp command surface` and DB schema markers to current through
    Phase 143;
  - lists `/rp canon add/list/group | /rp canon inspect <canon-id>`;
  - adds a Phase 143 capability note that the inspect command reads one existing
    `novel_canon` row by id and keeps deferred canon tools out of scope;
  - records that `get_canon(canon_id)` is read-only and command-visible only.
- `HERMES_TAVERN_DESIGN.md`
  - lists `/rp canon inspect <canon-id>` in the current writing/canon command
    surfaces;
  - rewords the stale Phase 9 add/list/group-only sentence while preserving
    `/rp canon check`, `/rp canon conflict`, `/rp canon pin <fact>`, and canon
    correlation as deferred.

No schema text was changed beyond the current-through marker; existing
`novel_canon` remains the storage contract.

## 6. Requirement and roadmap writeback

No requirement or roadmap writeback is required:

- The feature design has no `requirement`, `roadmap`, or `roadmap_item`
  frontmatter.
- The accepted slice is a bounded command-surface gap over an existing canon
  object model, not a new product vision or roadmap item.

## 7. Controller-run verification evidence

Controller reran verification after the executor draft and after controller
status/doc polishing:

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py` — passed with no output.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` — 338 passed in 13.30s.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` — 1029 passed in 47.19s.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` — 1029 passed in 44.67s.
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase143-canon-inspect-surface/design.md --require doc_type --require status --require feature` — passed.
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase143-canon-inspect-surface/hermes-tavern-phase143-canon-inspect-surface-acceptance.md --require doc_type --require status --require feature` — passed.
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-06-hermes-tavern-phase143-canon-inspect-surface/checklist.yaml` — passed.
- Protected core/runtime/source reverse-scope guards — empty as expected.
- Deferred `/rp canon check|conflict|pin` source/README guard — empty as expected.
- Prompt/provider/generation/importer `canon inspect|get_canon` guard — empty as expected.
- Stale-doc wording guard for `current through Phase 140`, `only add/list/group are included in Phase 9`, and bare `/rp canon add/list/group` — empty as expected.
- Current-doc literal guard for `/rp canon inspect <canon-id>` — non-empty in both architecture and root design.
- `git diff --check` — passed.

## 8. Attention candidates

No `attention.md` update is required. The only reusable convention is already
captured in the feature artifacts: future canon analysis commands must be scoped
as separate features and must preserve provider/safety/retrieval boundaries.

## 9. Residual deferred work

The following remain intentionally deferred and require fresh CodeStable design
before implementation:

- `/rp canon check`
- `/rp canon conflict`
- `/rp canon pin <fact>`
- canon correlation/automatic extraction/graph tooling
- retrieval/vectorization coupling
- provider/model/generation behavior
- archive/import/ZIP workflows
- safety-policy changes

## 10. Executor JSONL note

The executor JSONL contains one harmless failed pre-create read of the acceptance
report path before the file existed. The executor recovered, created the file,
and controller validators/tests/reverse-scope guards passed after final status
polishing.
