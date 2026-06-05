---
doc_type: feature-design
feature: "2026-06-06-hermes-tavern-phase138-scene-beat-metadata"
status: approved
date: "2026-06-06"
summary: >
  Scene Beat Metadata v1 adds local user-authored scene beat rows managed through
  /rp scene beat ... commands and optional project Markdown export visibility.
  Beats remain metadata-only/inert and do not affect prompts, active sessions,
  provider/model routing, content mode, credentials, retrieval/vectorization,
  generation, media, archive, graph, automatic extraction, or safety behavior.
tags: [novel, scene-beats, metadata, export, offline]
---

# Phase 138: Scene Beat Metadata v1

## 0. Terms

| Term | Meaning | Conflict guard |
|---|---|---|
| Scene Beat Metadata | A user-authored local note for one planned moment inside an existing scene. | Not generated beats, outline rewriting, prompt context, or execution state. |
| Beat Label | A compact one-token user label such as `arrival`, `reveal`, or `turning-point`. | Not a character name, relationship edge, canon fact, route key, or safety classifier. |
| Beat Text | Freeform user-authored prose describing the beat. | Not a prompt module, memory fact, retrieval document, provider instruction, or generated summary. |

Startup inspection found no active planned/pending/in-progress/draft feature checklist under `design/codestable/features`. Phase 137 is accepted. Source/docs/tests search found no `novel_scene_beats`, no `/rp scene beat ...` command, and no scene-beat tests.

## 1. Decisions And Constraints

### Need

The root design still lists beats as a deferred novel-engine dimension after Phase 121-137 made project, chapter, scene, summary, style, relationship, character, location, organization, plot-thread, style-sample, and default-binding metadata current. Scene beats are the smallest safe next slice because they attach to an existing scene and do not require a volume/arc hierarchy, graph model, archive format, generation workflow, or automatic extraction decision.

### Success

- A user can add a scene beat for an existing scene with a compact label and freeform beat text.
- A user can list beats for an explicit scene.
- A user can inspect, update, and delete a beat row by ID.
- Project Markdown export includes scene beats only under their owning scene and only when rows exist.
- `/rp help` and README Core commands expose the new scene beat command literals.
- Focused no-leak tests prove distinctive beat text does not appear in `/rp debug prompt` or `/rp debug context`.
- Implementation stays local/offline and does not change prompt, session, provider, content-mode, credential, retrieval, vectorization, media, archive, or generation behavior.

### Explicit Non-Goals

- No beat generation, rewrite, expand, compress, scoring, automatic extraction, or assistant-turn update cycle.
- No prompt module injection and no changes to scene-goal, scene-narration, project-style, canon, note, memory, lore, prompt compiler, debug prompt, debug context, or context-budget behavior.
- No volume, arc, chapter beat, project beat, beat ordering command, label rename, relationship graph, relationship rename, canon check/conflict/pin, or automatic default-binding application.
- No project archive ZIP/import/export, Markdown import, ST card/preset/lorebook/persona importer/exporter changes, cloud/collaboration, backend accounts, provider calls, credential persistence, retrieval/vectorization, media/TTS/image, or generation behavior.
- No age, date-of-birth, minor/underage, school-grade, sexual-safety classification fields, examples, tests, or commands.
- No edits to `run_agent.py`, `cli.py`, `gateway/run.py`, or `src/hermes_tavern/runtime.py`.

### Complexity

Small local plugin slice. It extends the existing scene metadata pattern in `db_novel.py`, `runtime_novel.py`, `commands.py`, README, and focused tests. It does not need a new top-level command family or runtime dispatch shim because it lives under the existing `/rp scene ...` command.

## 2. Names And Flow

### 2.1 Noun Layer

Current:

- `src/hermes_tavern/db_novel.py` owns novel project/chapter/scene persistence and Markdown export.
- `src/hermes_tavern/runtime_novel.py` owns `/rp scene ...` command behavior.
- `src/hermes_tavern/commands.py` owns help literals for `/rp scene ...`.
- `README.md` and focused command/docs tests guard public command visibility.
- No current beat table, helpers, commands, docs, or tests exist.

Change:

Add local scene-scoped metadata:

    novel_scene_beats(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      scene_id INTEGER NOT NULL REFERENCES novel_scenes(id) ON DELETE CASCADE,
      label TEXT NOT NULL,
      beat_text TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    )

    CREATE INDEX idx_novel_scene_beats_scene
      ON novel_scene_beats(scene_id, id)

Expected store helpers:

- `create_scene_beat(scene_id, label, beat_text)`
- `list_scene_beats(scene_id)`
- `get_scene_beat(beat_id)`
- `update_scene_beat(beat_id, beat_text)`
- `delete_scene_beat(beat_id)`

Rules:

- `scene_id` must reference an existing local scene.
- Blank label and blank beat text are rejected.
- Labels are immutable in v1; update changes `beat_text` only.
- List/export order is deterministic by `id ASC`.
- Missing scene returns bounded `No novel scene found: <id>` command behavior.
- Missing beat returns bounded `No scene beat found: <id>` command behavior.

### 2.2 Orchestration Layer

Flow:

    /rp scene beat add <scene-id> <label> <beat...>
      -> validate existing scene
      -> insert local beat row
      -> return compact confirmation

    /rp scene beat list <scene-id>
      -> validate existing scene
      -> list rows ordered by id
      -> return compact mobile output

    /rp scene beat inspect <beat-id>
      -> fetch row
      -> return compact detail

    /rp scene beat update <beat-id> <beat...>
      -> update beat_text only
      -> return compact confirmation

    /rp scene beat delete <beat-id>
      -> delete row
      -> return compact confirmation or not-found

    /rp project export [id]
      -> export_project_markdown(project_id)
      -> under each owning scene, emit optional Scene beats block before session messages

Flow constraints:

- Beat commands do not start, pause, resume, switch, archive, or mutate active sessions.
- Beat metadata is not selected by `_session_prompt_modules`, prompt compiler, debug prompt/context, context-budget reporting, model routing, memory, retrieval/vectorization, provider adapters, image/TTS/media flows, or generation.
- Export reads beat rows only during local Markdown export.

### 2.3 Mount Points

Allowed S1 files:

| File | Purpose |
|---|---|
| `src/hermes_tavern/db_novel.py` | Add `novel_scene_beats`, CRUD/list helpers, and optional per-scene Markdown export block. |
| `src/hermes_tavern/runtime_novel.py` | Add `/rp scene beat ...` parsing and bounded command messages. |
| `src/hermes_tavern/commands.py` | Add `/rp scene beat ...` help literals to the existing scene command entry. |
| `README.md` | Add Core command literals. |
| `tests/test_hermes_tavern_novel_db.py` | Add migration, CRUD, validation, missing-owner, export inclusion/omission/order tests. |
| `tests/test_hermes_tavern_novel_runtime.py` | Add command, usage/not-found, help, and no-leak tests. |
| `tests/test_hermes_tavern_commands.py` | Add help visibility assertions. |
| `tests/test_hermes_tavern_readme_docs.py` | Add README literal assertions. |

Prohibited S1 files:

- `run_agent.py`
- `cli.py`
- `gateway/run.py`
- `src/hermes_tavern/runtime.py`
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
- Any CodeStable checklist, acceptance, or status file during S1

### 2.4 Slicing

S1 only: implement local scene beat metadata persistence, commands, help/README literals, optional Markdown export visibility, and focused tests. Do not mark checklist or acceptance done.

Architecture/root-design writeback and acceptance closure are controller-owned later work.

### 2.5 Structure Health

No pre-feature micro-refactor.

`db_novel.py` and `runtime_novel.py` are broad, but they already own novel persistence/export and scene command families. This phase adds one narrow table and one nested scene subcommand. A new module or broad metadata abstraction would add risk and indirection beyond the requested one-pass executor slice.

## 3. Acceptance Criteria

1. Migration creates `novel_scene_beats` with `scene_id`, `label`, `beat_text`, timestamps, and `idx_novel_scene_beats_scene`.
2. Store helpers create, list, inspect, update, and delete scene beat rows with deterministic `id ASC` ordering.
3. Store helpers reject missing scenes, blank labels, and blank beat text with bounded behavior.
4. `/rp scene beat add/list/inspect/update/delete` commands exist in help output and return compact local metadata messages.
5. README Core commands and command/docs tests include the scene beat literals.
6. `/rp project export [id]` emits scene beats only under the owning scene and omits beat blocks when none exist.
7. Beat marker text does not appear in `/rp debug prompt`, `/rp debug context`, prompt modules, context-budget output, provider routing, content mode, retrieval/vectorization, or generation paths.
8. Focused and plugin-wide offline tests pass without network/provider calls.
9. Reverse-scope checks show no protected core, `runtime.py`, prompt/debug/context-budget, provider/model/content/generation/credential, retrieval/vectorization, memory, media/TTS/image, importer, plugin shim, build artifact, architecture/root-design, archive, graph, automatic extraction, or safety-bypass changes.

## 4. Verification Commands

S1 executor verification:

    PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider
    git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_manager.py src/hermes_tavern/runtime_debug.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_model.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/runtime_content.py src/hermes_tavern/memory.py src/hermes_tavern/runtime_memory.py src/hermes_tavern/images.py src/hermes_tavern/runtime_images.py src/hermes_tavern/importers plugins build/lib design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md
    git diff --check

Controller artifact validation after writing this artifact:

    python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase138-scene-beat-metadata/design.md --require doc_type --require status --require feature
    python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-06-hermes-tavern-phase138-scene-beat-metadata/checklist.yaml

## 5. Risks

- Beat terminology can imply generated outline or prompt behavior. Mitigation: command output, docs, tests, and no-leak checks keep beats metadata-only/inert.
- Scene export can accidentally show beats under the wrong scene. Mitigation: export must call `list_scene_beats(scene["id"])` inside the scene loop and test cross-scene exclusion.
- Additional ordering controls can expand scope. Mitigation: v1 uses insertion order by `id ASC`; explicit reordering is deferred.

## 6. Rollback

Remove the `novel_scene_beats` migration/index, store helpers, `/rp scene beat ...` command handling/help literals, README command lines, Markdown export block, and focused tests. With no prompt/session/provider/runtime core changes, removing those surfaces returns behavior to Phase 137.

## 7. Non-Goals

- No prompt compilation, active session behavior, provider/model routing, content mode, credential handling, retrieval/vectorization, generation, media/TTS/image, archive import/export, ST importer/exporter, cloud/collab, graph, automatic extraction, canon check/conflict/pin, automatic default-binding application, volume/arc, revision notes, or safety-bypass behavior.
- No protected core-file edits and no `src/hermes_tavern/runtime.py` edit.
