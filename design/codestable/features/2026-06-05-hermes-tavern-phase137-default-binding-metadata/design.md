---
doc_type: feature-design
status: draft
feature: "2026-06-05-hermes-tavern-phase137-default-binding-metadata"
date: "2026-06-05"
summary: >
  Default Binding Metadata v1 adds local, command-managed project/chapter/scene
  default binding rows for card, preset, lorebook, and persona assets, with
  command and Markdown export visibility only. It does not auto-apply bindings
  to prompts, sessions, provider routing, content mode, or generation.
tags: [novel, metadata, bindings, export, offline]
---

# Phase 137: Default Binding Metadata v1

## Terms

| Term | Meaning | Conflict guard |
|---|---|---|
| Default Binding Metadata | Local rows that record a user's intended default card, preset, lorebook, or persona for a project, chapter, or scene. | Not automatic prompt binding, not session start behavior, and not provider/model routing. |
| Binding Scope | One of `project`, `chapter`, or `scene`, with an existing local row ID. | Not cross-project collaboration, cloud sync, archive import/export, or graph inference. |
| Binding Asset | One of `card`, `preset`, `lorebook`, or `persona`, resolved against existing imported asset tables. | Not ST importer/exporter changes and not asset mutation. |

Startup inspection found no active planned, pending, in-progress, or draft feature
checklist under `design/codestable/features`. Legacy checklists without top-level
status are historical: recent architecture and checklist verification history show
their work as implemented, completed, done, or accepted. Phase 136 is accepted.

## Decisions/Constraints

Current state:

- `src/hermes_tavern/db_novel.py` owns project/chapter/scene metadata tables and Markdown export.
- `src/hermes_tavern/runtime_novel.py` owns novel command families.
- `src/hermes_tavern/commands.py`, `README.md`, and command/docs tests keep the mobile command surface visible.
- `design/HERMES_TAVERN_DESIGN.md` still lists `default_card_id`, `default_preset_id`, `default_lorebook_ids`, and default-binding metadata as deferred.

Change:

- Add one metadata table, expected name `novel_default_bindings`.
- Store one binding row per `(scope_type, scope_id, asset_type)` with an `asset_id` string and timestamps.
- Supported scopes are exactly `project`, `chapter`, and `scene`.
- Supported assets are exactly `card`, `preset`, `lorebook`, and `persona`.
- Commands expose set/list/inspect/clear behavior through `/rp binding ...`.
- Markdown project export adds an optional `## Default Bindings` section when rows exist for the exported project, its chapters, or its scenes.
- Command output and docs must say the rows are metadata-only.

Hard constraints:

- No automatic prompt module selection.
- No `/rp start`, `/rp scene start`, active-session, prompt compiler, debug prompt, debug context, context-budget, provider, model-router, content-mode, credential, generation, memory, summarization, vectorization, retrieval, media, TTS, image, cloud, collaboration, or archive behavior changes.
- No ST card/preset/lorebook/persona importer or exporter changes.
- No protected core edits to `run_agent.py`, `cli.py`, or `gateway/run.py`.
- Fixtures remain neutral fictional writing metadata and avoid age-related fields or examples.
- Adult-fiction/RP compatibility is preserved without safety bypass behavior.

## Names/Flow

### Noun Layer

Expected table:

```sql
novel_default_bindings(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scope_type TEXT NOT NULL,
  scope_id INTEGER NOT NULL,
  asset_type TEXT NOT NULL,
  asset_id TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(scope_type, scope_id, asset_type)
)
CREATE INDEX idx_novel_default_bindings_scope
  ON novel_default_bindings(scope_type, scope_id)
```

Expected store helpers:

- `set_default_binding(scope_type, scope_id, asset_type, asset_id)`
- `list_default_bindings(scope_type, scope_id)`
- `list_default_bindings_for_project(project_id)`
- `get_default_binding(binding_id)`
- `clear_default_binding(binding_id)`

Validation:

- Scope must exist.
- Chapter and scene export visibility must be constrained to the exported project.
- Asset must exist in the current local store.
- Invalid scope/asset values return bounded command usage or bounded not-found messages.

### Orchestration Layer

Command flow:

```text
/rp binding set <project|chapter|scene> <scope-id> <card|preset|lorebook|persona> <asset-id>
  -> validate scope type/id
  -> validate asset type/id
  -> upsert metadata row
  -> return bounded metadata-only confirmation

/rp binding list <project|chapter|scene> <scope-id>
  -> validate scope
  -> list rows ordered by asset_type/id
  -> return compact mobile output

/rp binding inspect <binding-id>
  -> fetch row
  -> resolve display names where available
  -> return metadata-only detail

/rp binding clear <binding-id>
  -> delete row
  -> return bounded confirmation or not-found
```

Export flow:

```text
/rp project export [id]
  -> export_project_markdown(project_id)
  -> collect bindings for project, its chapters, and its scenes
  -> optional ## Default Bindings section
  -> existing local MEDIA export contract unchanged
```

Suggested export placement:

```text
Summary
Project Brief
Outline
Default Bindings
Style Guide
Style Samples
Locations
Organizations
Plot Threads
Characters
Relationships
Chapters
Canon
Timeline
```

The section is omitted when no relevant binding rows exist.

### Structure Health

No pre-feature micro-refactor.

`db_novel.py` and `runtime_novel.py` are large, but recent metadata phases already
use these files for bounded novel metadata additions. A broader split would be a
separate refactor and is not required for this slice.

## Acceptance Criteria

1. Migration creates `novel_default_bindings`, unique scope/asset constraint, and scope index.
2. Store helpers set, replace, list, inspect, and clear binding rows for project, chapter, and scene scopes.
3. Store helpers validate missing scopes and missing assets with bounded behavior.
4. `/rp binding set/list/inspect/clear` commands exist in help output and return compact metadata-only messages.
5. `README.md` core commands and command/docs tests include the binding literals.
6. `/rp project export [id]` emits optional `## Default Bindings` only when relevant rows exist.
7. Project export includes project, chapter, and scene binding rows belonging to the exported project and excludes rows from other projects.
8. Binding marker text does not appear in `/rp debug prompt`, `/rp debug context`, active prompt modules, provider routing, or generation paths.
9. Focused and plugin-wide offline tests pass without network/provider calls.
10. Reverse-scope checks show no protected core, build artifact, provider, model-router, content-mode, generation, credential, retrieval/vectorization, automation, media/TTS/image, cloud/collab, archive, ST importer/exporter, graph, automatic extraction, or safety-bypass changes.

## Verification Commands

S1 focused verification:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider
git diff --name-only -- run_agent.py cli.py gateway/run.py build/lib
git diff --check
```

S2 acceptance/writeback verification:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider
python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-05-hermes-tavern-phase137-default-binding-metadata/design.md --require doc_type --require status --require feature
python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-05-hermes-tavern-phase137-default-binding-metadata/checklist.yaml
git diff --check
```

## Risks

- “Default” terminology can imply automatic application.
  Mitigation: command output, docs, architecture, and tests must explicitly keep this metadata-only.
- A polymorphic scope table can accidentally export unrelated chapter/scene rows.
  Mitigation: `list_default_bindings_for_project(project_id)` must constrain rows through project ownership.
- Asset IDs can become stale if an asset is deleted later.
  Mitigation: this phase validates on set and displays missing assets defensively on inspect/export; cascading asset deletion is out of scope.

## Rollback

Remove the `/rp binding` command entry and runtime handler, remove the
`novel_default_bindings` migration/helpers/export section, and remove the focused
tests/docs. Existing project, chapter, scene, card, preset, lorebook, persona,
prompt, provider, and generation behavior returns to the Phase 136 state.

## Non-goals

- No automatic prompt/session/default asset application.
- No multi-lorebook ordering semantics beyond one metadata row per scope and asset type.
- No project archive ZIP/import/export, Markdown import, ST asset importer/exporter, relationship graph/rename, automatic extraction, generated metadata, canon policy, or content-mode metadata.
- No provider calls, cloud sync, collaboration, credential persistence, model routing, tokenizer, vectorization, retrieval, summarization, media, TTS, image, or generation behavior.
- No protected core-file edits.
