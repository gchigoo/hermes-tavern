---
doc_type: feature-design
feature: "2026-06-06-hermes-tavern-phase140-relationship-label-rename"
status: approved
date: "2026-06-06"
summary: >
  Relationship Label Rename adds a local command to rename the label of an
  existing relationship-state metadata row through /rp relationship rename
  <relationship-id> <label>. The slice is metadata-only/inert: it changes only
  command/list/inspect/export-visible local label text and does not alter prompts,
  active sessions, provider/model routing, content mode, credentials,
  retrieval/vectorization, generation, media, archive, graph, automatic extraction,
  plugin shims, or safety behavior.
tags: [novel, relationships, metadata, commands, export, offline]
---

# Phase 140: Relationship Label Rename

## 0. Terms

| Term | Meaning | Conflict guard |
|---|---|---|
| Relationship Label Rename | Updating the user-facing label on one existing `novel_relationship_states` row. | Not relationship graph modeling, alias management, merge/split, extraction, or generated rewriting. |
| Relationship Label | The compact text shown in `/rp relationship list`, `/rp relationship inspect`, and Markdown export for one relationship-state row. | Not a stable public identifier, not a route key, not a graph node, and not prompt context. |
| Relationship State Text | The existing prose state stored in `state_text`. | Not changed by rename; existing `/rp relationship update` remains state-text-only. |

Startup inspection found no active planned/pending/in-progress/draft checklist under `design/codestable/features`. Phase 139 is accepted. Source search found current `/rp relationship add/list/inspect/update/delete` behavior, no `/rp relationship rename ...` literal, and no `rename_relationship_state` helper.

## 1. Decisions And Constraints

### Need

Relationship-state metadata is now current, export-visible, and command-managed. The root design still lists relationship graph/rename/automatic extraction among deferred novel-engine dimensions. Graph and automatic extraction are unsafe for unattended implementation because they imply semantics, inference, or update-cycle behavior. A label-only relationship rename is the smallest safe part of that deferred area: it lets users correct or clarify a relationship label without deleting and recreating the row, while preserving id, ordering, project ownership, and state text.

### Success

- A user can run `/rp relationship rename <relationship-id> <label>` for an existing relationship-state row.
- The command updates only `novel_relationship_states.label` and `updated_at`.
- `/rp relationship list`, `/rp relationship inspect`, and project Markdown export show the new label.
- Existing `/rp relationship update <relationship-id> <state...>` remains state-text-only.
- Blank labels, missing relationship IDs, and malformed IDs return bounded local messages.
- `/rp help` and README Core commands include the nested relationship rename literal.
- Focused no-leak tests prove distinctive renamed label text does not appear in `/rp debug prompt` or `/rp debug context`.
- Implementation stays local/offline and does not touch `src/hermes_tavern/runtime.py` or protected core/plugin/build paths.

### Explicit Non-Goals

- No relationship graph, nodes, edges, inverse relationships, aliases, merge/split, cardinality, scoring, or graph export.
- No automatic extraction, summarization, assistant-turn update cycle, refresh worker, or generated relationship edits.
- No prompt module injection and no changes to debug prompt/context, context-budget reporting, model routing, provider adapters, content mode, credentials, generation, memory, retrieval/vectorization, media/TTS/image, archive/import/export formats, ST importers/exporters, or safety behavior.
- No top-level `/rp relationship-rename ...`, `/rp rel ...`, or new runtime dispatch shim.
- No schema migration or new table.
- No edits to `src/hermes_tavern/runtime.py`, `run_agent.py`, `cli.py`, `gateway/run.py`, `plugins/**`, or `build/lib/**`.
- No new content-safety classifier fields, examples, tests, or provider-safety bypass behavior.

### Complexity

Small local plugin slice. It extends the existing relationship metadata path in `db_novel.py`, `runtime_novel.py`, `commands.py`, README, and focused tests. It does not require new architecture, a new top-level command family, schema changes, prompt integration, model/provider work, or importer/exporter compatibility choices.

## 2. Names And Flow

### 2.1 Noun Layer

Current:

- `src/hermes_tavern/db_novel.py` owns `novel_relationship_states` persistence.
- `src/hermes_tavern/runtime_novel.py` owns `/rp relationship ...` command handling.
- `src/hermes_tavern/commands.py` owns `/rp help` literals for the existing `relationship` command family.
- `README.md` and focused command/docs tests guard public command visibility.
- `novel_relationship_states` already has `id`, `project_id`, `label`, `state_text`, `created_at`, and `updated_at`.
- Existing update behavior changes `state_text` only; labels are effectively immutable after add.

Change:

Add one store helper:

    rename_relationship_state(relationship_id, label)

Rules:

- `relationship_id` must identify an existing `novel_relationship_states` row.
- `label` is stripped before persistence.
- Blank new labels are rejected with `ValueError("Relationship label cannot be blank")`.
- Missing rows are rejected with `ValueError("Relationship state not found")`.
- The helper updates only `label` and `updated_at`.
- It does not change `id`, `project_id`, `state_text`, `created_at`, ordering, or export placement.

No schema change is required.

### 2.2 Orchestration Layer

Flow:

    /rp relationship rename <relationship-id> <label>
      -> existing relationship_command route
      -> parse relationship id
      -> join remaining args as the new label
      -> rename local row label only
      -> return compact confirmation

Follow-on visibility is passive:

    /rp relationship list [project-id]
      -> shows renamed label through existing list path

    /rp relationship inspect <relationship-id>
      -> shows renamed label through existing inspect path

    /rp project export [id]
      -> shows renamed label in existing ## Relationships export block

Flow constraints:

- Rename commands do not start, pause, resume, switch, archive, clone, or mutate active sessions.
- Rename does not create another relationship row and does not delete history.
- Rename does not change relationship state text; `/rp relationship update` remains the only state-text update command.
- Relationship labels remain excluded from prompt modules, prompt compiler, debug prompt/context, context-budget reporting, model routing, memory update cycles, retrieval/vectorization, provider adapters, image/TTS/media flows, and generation.

### 2.3 Mount Points

Allowed S1 files:

| File | Purpose |
|---|---|
| `src/hermes_tavern/db_novel.py` | Add `rename_relationship_state` helper; no migration or schema change. |
| `src/hermes_tavern/runtime_novel.py` | Add `/rp relationship rename ...` parsing and bounded command messages under the existing relationship command family. |
| `src/hermes_tavern/commands.py` | Add `/rp relationship rename <relationship-id> <label>` help literal to the existing `relationship` entry only. |
| `README.md` | Add the Core command literal. |
| `tests/test_hermes_tavern_novel_db.py` | Add helper tests for rename success, missing row, blank label, state-text preservation, and updated timestamp. |
| `tests/test_hermes_tavern_novel_runtime.py` | Add command tests for rename success, usage/not-found behavior, state-text preservation, list/inspect/export visibility, and no prompt/debug/context leak. |
| `tests/test_hermes_tavern_commands.py` | Add help visibility assertion and guard against new top-level rename/relationship-rename route. |
| `tests/test_hermes_tavern_readme_docs.py` | Add README literal assertion. |

Prohibited S1 files:

- `src/hermes_tavern/runtime.py`
- `run_agent.py`
- `cli.py`
- `gateway/run.py`
- `src/hermes_tavern/runtime_prompt_modules.py`
- `src/hermes_tavern/prompt.py`
- `src/hermes_tavern/runtime_prompt_manager.py`
- `src/hermes_tavern/runtime_debug.py`
- `src/hermes_tavern/model_router.py`
- `src/hermes_tavern/provider_bridge.py`
- `src/hermes_tavern/adapters.py`
- `src/hermes_tavern/runtime_model.py`
- `src/hermes_tavern/runtime_generation.py`
- `src/hermes_tavern/runtime_content.py`
- `src/hermes_tavern/memory.py`
- `src/hermes_tavern/runtime_memory.py`
- `src/hermes_tavern/images.py`
- `src/hermes_tavern/runtime_images.py`
- `src/hermes_tavern/importers/**`
- `plugins/**`
- `build/lib/**`
- `design/codestable/architecture/ARCHITECTURE.md`
- `design/HERMES_TAVERN_DESIGN.md`
- Any CodeStable checklist, acceptance, status, architecture, or root-design writeback during S1

### 2.4 Slicing

S1 only: implement the local relationship-label rename helper, command route, help/README literals, and focused tests.

S1 must not mark the feature accepted, create an acceptance report, update architecture, update root design, or finalize checklist statuses. Controller-owned acceptance/writeback can happen later after implementation verification.

### 2.5 Structure Health

No pre-feature micro-refactor.

`db_novel.py` and `runtime_novel.py` are broad, but they already own relationship metadata persistence and the `/rp relationship ...` command family. This phase adds one helper and one branch to existing local patterns. A new module, graph abstraction, or route shim would add risk and violate the narrow metadata-only phase boundary.

## 3. Acceptance Criteria

1. `rename_relationship_state(relationship_id, label)` exists and updates only `label` and `updated_at` on `novel_relationship_states`.
2. The rename helper preserves `id`, `project_id`, `state_text`, `created_at`, and existing row ordering.
3. Blank new labels and missing relationship IDs return bounded behavior.
4. `/rp relationship rename <relationship-id> <label>` works through existing relationship command routing.
5. Existing `/rp relationship update <relationship-id> <state...>` remains state-text-only and does not alter labels.
6. `/rp relationship list`, `/rp relationship inspect`, and `/rp project export [id]` show the renamed label through existing read/export paths.
7. `/rp help`, `TAVERN_COMMAND_TABLE`, README Core commands, and docs tests include the relationship rename literal.
8. No new top-level route is added for relationship rename.
9. Distinctive renamed label text does not appear in `/rp debug prompt`, `/rp debug context`, prompt modules, context-budget output, provider routing, content mode, retrieval/vectorization, or generation paths.
10. Focused and plugin-wide offline tests pass without network/provider calls.
11. Reverse-scope checks show no protected core, `runtime.py`, prompt/debug/context-budget, provider/model/content/generation/credential, retrieval/vectorization, memory, media/TTS/image, importer, plugin shim, build artifact, architecture/root-design, archive, graph, automatic extraction, or safety-bypass changes.

## 4. Verification Commands

S1 executor verification:

    PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider
    git diff --name-only -- src/hermes_tavern/runtime.py run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_manager.py src/hermes_tavern/runtime_debug.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_model.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/runtime_content.py src/hermes_tavern/memory.py src/hermes_tavern/runtime_memory.py src/hermes_tavern/images.py src/hermes_tavern/runtime_images.py src/hermes_tavern/importers plugins build/lib design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md
    git diff --check

Controller artifact validation after writing this artifact:

    python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase140-relationship-label-rename/design.md --require doc_type --require status --require feature
    python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-06-hermes-tavern-phase140-relationship-label-rename/checklist.yaml

## 5. Risks

- Rename may drift into graph or alias semantics. Mitigation: helper updates only the existing label column; no new schema, graph fields, alias tables, merge/split, or extraction behavior.
- Routing may accidentally require `runtime.py`. Mitigation: keep command under the existing `relationship` command table entry and `relationship_command` branch only.
- Existing export visibility could be missed. Mitigation: add tests proving Markdown export shows the renamed label without export code changes beyond what is actually necessary.
- Debug/prompt leakage can occur if future relationship metadata paths change. Mitigation: add distinctive renamed-label no-leak tests for `/rp debug prompt` and `/rp debug context`.

## 6. Rollback

Remove `rename_relationship_state`, the `/rp relationship rename ...` branch, the help/README literal, and focused tests. Since there is no schema migration, prompt path, provider path, runtime-core edit, plugin shim edit, or build artifact edit, rollback returns behavior to Phase 139 by removing the command surface and helper only.

## 7. Non-Goals

- No relationship graph, aliases, merge/split, inverse edges, graph export, graph query, automatic extraction, generated relationship updates, archive/import, ST importer/exporter changes, prompt compilation, active-session behavior, provider/model routing, content mode, credential handling, retrieval/vectorization, generation, media/TTS/image, cloud/collab, or safety-bypass behavior.
- No top-level route family and no `src/hermes_tavern/runtime.py` edit.
- No architecture/root-design/checklist acceptance finalization during S1.