---
doc_type: feature-design
status: approved
feature: "2026-06-08-hermes-tavern-phase167-project-json-export"
date: "2026-06-08"
summary: >
  Phase 167 adds one bounded /rp project export json <project-id> command that
  exports all project entities (chapters, scenes, canon, timeline, relationships,
  character states, locations, organizations, plot threads, style samples,
  scene beats, revision notes) as individual JSON files under a project-named
  export directory, following the Phase 149–166 export pattern. Returns a
  summary with file paths. No schema, prompt, provider, generation,
  content-mode, or safety behavior changes.
tags: [hermes-tavern, project, export, json, bundle, offline]
owner: codestable-cron
---

# Phase 167: Project JSON Bundle Export

## Background

Phases 149–166 added individual JSON export commands for 17 entity types:
cards, lorebooks, presets, personas, sessions, chapters, scenes, canon,
timeline, relationships, character states, locations, organizations, plot
threads, style samples, default bindings, scene beats, and revision notes.
Each exports one stored entity to a profile-safe local JSON file and returns
`file:` plus quoted `MEDIA:"<path>"`.

Phase 121 added `/rp project export [id]` which produces a Markdown file.
There is no way to export all project entities as JSON files in one operation.
Users who want to backup or transfer a complete project must run 10+
individual export commands.

## Scope

Add one export subcommand to the existing project export command family:

- `/rp project export json <project-id>`
- Resolve `<project-id>` via the existing `_resolve_project_id(...)` helper.
- Verify the project exists via `runtime.store.get_project(project_id)`.
- Create an export directory at
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "projects" / "<project-id>"`
- For each entity type with data, call the existing individual export
  functions to write JSON files into the project export directory.
- Return a bounded summary listing exported entity types, counts, and
  the export directory path, with `MEDIA` for the directory.
- No schema, table/index migrations, prompt, provider, generation,
  credential, content-mode, or safety behavior changes.

Exported entity types (project-level, skip card/lorebook/preset/persona/session which are not project-scoped):

| Entity | Export function / source |
|--------|--------------------------|
| Chapters | `chapter_export()` × each chapter |
| Scenes | `scene_export()` × each scene |
| Canon | `canon_export()` × each canon entry |
| Timeline | `timeline_export()` × each timeline event |
| Relationships | `relationship_export()` × each relationship |
| Character states | `character_state_export()` × each character state |
| Locations | `location_export()` × each location |
| Organizations | `organization_export()` × each organization |
| Plot threads | `plot_thread_export()` × each plot thread |
| Style samples | `style_sample_export()` × each style sample |
| Default bindings | `binding_export()` × each binding |
| Scene beats | `scene_beat_export()` × each scene beat |
| Revision notes | `project_revision_export()` × each revision note |

## Non-goals / Boundaries

Do not change any schema, table/index migration, entity CRUD, prompt
compiler, provider/model routing, generation settings, credentials,
content-mode, project archive, plugin registration, gateway/core files,
or build artifacts.

This phase does not implement:
- Card/lorebook/preset/persona/session export in the project bundle
  (these are not project-scoped assets)
- ZIP/tar archive packaging
- Cloud sync or remote transfer
- Import from bundle
- Incremental/delta export
- Export format selection

## Design

### Command routing

Add a `json` subcommand branch inside the existing `project_export()`
function (in `runtime_novel.py`), after the existing Markdown export path.
If `command.args[1] == "json"`, route to the new bundle export function.

### Bundle export function

```python
def project_export_json(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id, err = _resolve_project_id(...)
    # Verify project exists
    # Create exports/projects/<project_id>/ directory
    # For each entity type: list entities, call individual export
    # Collect results (entity type, count, any errors)
    # Return summary with MEDIA for directory
```

### Export directory structure

```
<hermes_home>/plugins/hermes-tavern/exports/projects/<project_id>/
├── chapters/
│   ├── chapter_<id>.json
│   └── ...
├── scenes/
│   ├── scene_<id>.json
│   └── ...
├── canon/
│   ├── canon_<id>.json
│   └── ...
├── timeline/
│   ├── timeline_<id>.json
│   └── ...
├── relationships/
│   ├── relationship_<id>.json
│   └── ...
├── character_states/
│   ├── character_state_<id>.json
│   └── ...
├── locations/
│   ├── location_<id>.json
│   └── ...
├── organizations/
│   ├── organization_<id>.json
│   └── ...
├── plot_threads/
│   ├── plot_thread_<id>.json
│   └── ...
├── style_samples/
│   ├── style_sample_<id>.json
│   └── ...
├── bindings/
│   ├── binding_<id>.json
│   └── ...
├── scene_beats/
│   ├── scene_beat_<id>.json
│   └── ...
└── revision_notes/
    ├── note_<id>.json
    └── ...
```

### Summary output format

```
Project JSON export complete for project [<id>] "<title>".
Exported 13 entity types: 3 chapters, 7 scenes, 2 canon, 1 timeline,
2 relationships, 1 character state, 1 location, 1 organization,
2 plot threads, 3 style samples, 1 binding, 4 scene beats, 5 revision notes.
Directory: <path>
MEDIA:"<path>"
```

### Mount points

- `src/hermes_tavern/runtime_novel.py`: new `project_export_json()` function +
  `json` subcommand branch in `project_export()` (after Markdown path, before
  final return) + updated usage string
- `src/hermes_tavern/commands.py`: updated help_lines for project command
- `README.md`: Core commands table visibility
- `tests/test_hermes_tavern_novel_runtime.py`: focused bundle export tests

### Slicing

S1 implements the bundle export command, dispatcher branch, help, README,
and focused tests.
S2 is controller-owned verification, acceptance, and architecture/root-design
writeback.

## Acceptance Criteria

- `/rp project export json <project-id>` is visible in generated help and
  README Core commands.
- Exporting a project with entities creates a directory with subdirectories
  per entity type, each containing valid JSON files.
- The summary reports entity types and counts correctly.
- An empty project (no entities) creates the directory and reports zero counts.
- Not-found project IDs return "No novel project found: <id>".
- Malformed/missing project IDs return the project usage string.
- Existing `/rp project export [id]` Markdown behavior is unchanged.
- No prompt/debug/context-budget, provider/model, generation, credential,
  retrieval/vectorization, archive/import, plugin shim, build artifact, or
  protected Hermes core behavior changes.

## Architecture/Root Design Relationship

This slice completes the JSON export command surface from Phases 149–166 by
adding the project-level bundle export. Architecture/root-design writeback in
S2 should describe the new `/rp project export json <project-id>` command and
preserve existing deferred boundaries.

## Verification Commands

S1 executor verification:

    PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_readme_docs.py
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider
    git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_manager.py src/hermes_tavern/runtime_debug.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_model.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/runtime_content.py src/hermes_tavern/memory.py src/hermes_tavern/runtime_memory.py src/hermes_tavern/images.py src/hermes_tavern/runtime_images.py src/hermes_tavern/importers plugins build/lib design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md src/hermes_tavern/db_novel.py
    git diff --check
