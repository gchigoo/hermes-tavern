---
doc_type: feature-acceptance
feature: "2026-06-06-hermes-tavern-phase141-metadata-inertness-matrix"
status: accepted
date: "2026-06-06"
summary: >
  Phase 141 is accepted as test-only metadata no-leak co-presence regression
  hardening for current inert novel metadata families. It locks the existing
  contract that command/export-visible metadata stays out of debug prompt/context
  output when many families coexist in one linked runtime session.
tags: [novel, metadata, no-leak, regression, test-only, acceptance]
---

# Phase 141 Metadata Inertness Matrix Acceptance

> Phase: S2 verify/accept test-only phase
> Controller verification date: 2026-06-06
> Design: `design/codestable/features/2026-06-06-hermes-tavern-phase141-metadata-inertness-matrix/design.md`
> Checklist: `design/codestable/features/2026-06-06-hermes-tavern-phase141-metadata-inertness-matrix/checklist.yaml`

## 1. Interface, schema, and command contract

Phase 141 is accepted as regression hardening only. It introduces no new user
command, command grammar, SQLite schema/table/index/migration, runtime API,
provider path, export format, prompt module, context-budget behavior,
retrieval/vectorization path, generation path, credential handling, graph/alias /
merge/split behavior, archive/importer behavior, media behavior, or safety
behavior.

Accepted implementation surface:

- `tests/test_hermes_tavern_novel_runtime.py`

Accepted S2 status surface:

- this acceptance report
- `design/codestable/features/2026-06-06-hermes-tavern-phase141-metadata-inertness-matrix/checklist.yaml`

## 2. Behavior and scope evidence

S1 added exactly one co-presence runtime regression:

- `test_all_current_inert_metadata_markers_do_not_leak_to_debug_prompt_or_context`

The test creates a local `TavernStore` + `TavernRuntime`, saves a card-backed
active session, creates a project/chapter/scene, links the scene to the active
session, and sets an existing scene-goal prompt-active sentinel:

- `secure the lighthouse key before midnight.`

It then asserts `Scene goal: secure the lighthouse key before midnight.` appears
in `/rp debug prompt`. This makes the no-leak assertions meaningful: the linked
session prompt path is active rather than empty or unlinked.

## 3. No-leak matrix evidence

The accepted regression creates current inert metadata markers for all families
listed in the design and checks that each marker is absent from both `/rp debug
prompt` and `/rp debug context`:

- project brief premise
- project outline
- chapter summary
- scene summary
- relationship state text
- renamed relationship label
- character state
- location description
- organization description
- plot thread description
- style sample text
- revision note text
- scene beat text
- default-binding marker/content

This closes the cross-feature drift risk that per-family no-leak tests could
miss when many inert metadata families coexist on one linked project/chapter /
scene.

## 4. Reverse-scope boundaries

Controller inspection and reverse-scope guards confirmed S2 changed only the
feature status artifacts and did not touch runtime/product surfaces.

Protected surfaces kept unchanged during S2:

- `README.md`
- `src/**`
- `tests/**`
- `run_agent.py`
- `cli.py`
- `gateway/**`
- `plugins/**`
- `build/lib/**`
- `design/HERMES_TAVERN_DESIGN.md`
- `design/codestable/architecture/ARCHITECTURE.md`

Phase 141 also preserved the S1 prohibition against source fixes: if the matrix
had exposed a source bug, the correct next step would have been a separate issue
or feature slice, not widening this acceptance pass.

## 5. Architecture and root-design writeback

No architecture or root-design writeback was required. Design §4 defines Phase
141 as pure regression hardening for an existing current contract: recent local
metadata families are command/export-visible only and excluded from prompt,
debug/context, provider, retrieval/vectorization, generation, credential, and
content-mode paths.

Because Phase 141 adds no new stable capability and no new architecture-visible
runtime path, `design/codestable/architecture/ARCHITECTURE.md` and
`design/HERMES_TAVERN_DESIGN.md` remain unchanged.

## 6. Requirement and roadmap writeback

No requirement or roadmap writeback was required:

- The design frontmatter has no `requirement` field.
- The design frontmatter has no `roadmap` / `roadmap_item` fields.
- The phase is regression hardening for an already-current architecture contract,
  not a new product capability.

## 7. Controller verification evidence

Controller reran the verification ledger from scratch after the Codex executor
created the S2 draft artifacts:

| Command | Result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_novel_runtime.py` | passed; no output |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_runtime.py::test_all_current_inert_metadata_markers_do_not_leak_to_debug_prompt_or_context -q -o 'addopts=' -p no:cacheprovider` | passed; `1 passed in 0.38s` |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_runtime.py -q -o 'addopts=' -p no:cacheprovider` | passed; `169 passed in 9.09s` |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` | passed; `1015 passed in 45.99s` |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` | passed; `1015 passed in 43.41s` |
| `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase141-metadata-inertness-matrix/hermes-tavern-phase141-metadata-inertness-matrix-acceptance.md --require doc_type --require status` | passed after controller finalization |
| `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase141-metadata-inertness-matrix/design.md --require doc_type --require status` | passed |
| `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-06-hermes-tavern-phase141-metadata-inertness-matrix/checklist.yaml` | passed after controller finalization |
| `git diff --name-only -- README.md src tests run_agent.py cli.py gateway plugins build/lib design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md` | passed; empty output |
| `git diff --check` | passed |

The Codex architect read-only sandbox had one harmless failed sample-path probe
while looking for a nearby acceptance report and macOS read-only sandbox `git`
warnings from `xcrun` cache creation. The final artifact was valid and the
controller reran git/status/verification outside that sandbox.

## 8. Attention candidates

No new `attention.md` candidate was found. This slice reinforced an existing
workflow rule rather than discovering a new recurring environment/tooling rule.

## 9. Residual work

No residual work remains for Phase 141. Broader metadata/product ideas such as
new metadata families, prompt activation, graph semantics, aliases, merge/split,
automatic extraction, retrieval/vectorization, or generation behavior remain out
of scope and should be planned as separate CodeStable phases if needed.
