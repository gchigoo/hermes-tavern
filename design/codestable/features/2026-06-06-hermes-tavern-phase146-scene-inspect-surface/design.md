---
doc_type: feature-design
feature: "2026-06-06-hermes-tavern-phase146-scene-inspect-surface"
status: approved
date: "2026-06-06"
summary: >
  Phase 146 adds a read-only /rp scene inspect <scene-id> surface for existing
  novel_scenes rows, using the existing scene getter and preserving schema,
  scene ordering, scene start/linking, scene summary/goal/narration/beat mutation,
  prompt, provider, generation, retrieval/vectorization, credentials, content-mode,
  safety behavior, and protected core files.
tags: [hermes-tavern, scene, command-surface, read-only, offline]
created: "2026-06-06"
updated: "2026-06-06"
owner: codestable-cron
---

# Scene Inspect Surface

## Background

Current CodeStable history is accepted through Phase 145. Phases 143, 144, and
145 added bounded read-only inspect surfaces for canon, timeline, and chapter
rows. The scene family already has `/rp scene create/list/start`,
`/rp scene summary ...`, `/rp scene goal ...`, `/rp scene narration ...`, and
`/rp scene beat ...`, but it has no single-row scene inspection command.

This is the safest next bounded phase because `TavernStore.get_scene(scene_id)`
already exists and returns one `novel_scenes` row or `None`. S1 does not need a
schema change, DB helper, runtime shim, service lifecycle change, provider call,
or product decision.

## Scope

Add one read-only scene inspection surface:

- `/rp scene inspect <scene-id>` routes under the existing scene command family in
  `src/hermes_tavern/runtime_novel.py`.
- The command uses the existing `runtime.store.get_scene(scene_id)` helper.
- Generated `/rp help` and README Core commands include the new scene inspect literal.
- Focused runtime/help/README tests cover success, malformed ids, missing rows,
  and unchanged adjacent scene behavior.

## Non-goals / Boundaries

This phase does not add scene update, delete, renumbering, reparenting, archive
import/export ZIP, automatic extraction, prompt/debug/context-budget injection,
provider/model routing, generation, retrieval/vectorization, credential handling,
content-mode behavior, scene start/linking changes, scene summary mutation changes,
scene goal/narration/beat behavior changes, minors/underage behavior, or provider
safety-bypass behavior.

Do not edit `run_agent.py`, `cli.py`, `gateway/run.py`, `src/hermes_tavern/runtime.py`,
`src/hermes_tavern/db.py`, `src/hermes_tavern/db_novel.py`, prompt/provider/generation
files, importer files, `plugins/**`, or `build/lib/**`.

No paths are needed in S1. If later paths are needed in a separate phase, use
`get_hermes_home()` and never hard-code `~/.hermes`. No DB persistence changes
are allowed, and no api_key/access_token storage behavior may change.

## Proposed Design

The noun layer already exists:

`novel_scenes(id, chapter_id, session_id, title, summary, scene_number, status, created_at, updated_at)`

This slice does not create tables, alter indexes, mutate rows, or change
`list_scenes(chapter_id)` ordering.

The orchestration layer follows the accepted chapter inspect shape:

`/rp scene inspect <scene-id>` -> `TAVERN_COMMAND_TABLE["scene"]` ->
`TavernRuntime._scene_command` -> `runtime_novel.scene_command` ->
`scene_inspect` -> existing `TavernStore.get_scene`.

The command output should be compact and bounded. It should include scene id,
chapter id, scene number, title, status, linked session id or an explicit not-linked
marker, and a mobile-bounded summary preview or an explicit not-set marker.

Argument handling should match Phase 145 chapter inspect:

- Missing id, malformed id, non-positive id, and extra arguments return the scene
  usage string.
- A missing scene row returns a bounded not-found message.
- The implementation may factor the existing scene usage string into a private
  `_SCENE_USAGE` constant only to avoid duplicate text; the only usage text change
  is adding `/rp scene inspect <scene-id>`.

No micro-refactor is needed. `runtime_novel.py` already owns the scene command
family, and `commands.py` already owns generated help. This is a small family-local
extension and must not touch `src/hermes_tavern/runtime.py`.

## S1 Allowed Files

- `src/hermes_tavern/runtime_novel.py`
- `src/hermes_tavern/commands.py`
- `README.md`
- `tests/test_hermes_tavern_novel_runtime.py`
- `tests/test_hermes_tavern_commands.py`
- `tests/test_hermes_tavern_readme_docs.py`

## S1 Prohibited Files

- `run_agent.py`
- `cli.py`
- `gateway/run.py`
- `src/hermes_tavern/runtime.py`
- `src/hermes_tavern/db.py`
- `src/hermes_tavern/db_novel.py`
- `src/hermes_tavern/prompt.py`
- `src/hermes_tavern/runtime_prompt_modules.py`
- `src/hermes_tavern/model_router.py`
- `src/hermes_tavern/provider_bridge.py`
- `src/hermes_tavern/adapters.py`
- `src/hermes_tavern/runtime_generation.py`
- `src/hermes_tavern/importers/**`
- `plugins/**`
- `build/lib/**`
- `design/HERMES_TAVERN_DESIGN.md`
- `design/codestable/architecture/ARCHITECTURE.md`

## Acceptance Criteria

1. `/rp scene inspect <scene-id>` returns bounded details for one existing scene row.
2. Malformed ids, missing ids, non-positive ids, and extra args return the scene usage string.
3. A missing scene row returns a bounded not-found message without exceptions.
4. Generated help and README Core commands include `/rp scene inspect <scene-id>`.
5. Existing `/rp scene list <chapter-id>` ordering, `/rp scene start <scene-id>` linking, `/rp scene summary ...`, `/rp scene goal ...`, `/rp scene narration ...`, and `/rp scene beat ...` behavior remain unchanged.
6. `src/hermes_tavern/db_novel.py` and `TavernStore.get_scene(scene_id)` remain unchanged.
7. No schema, prompt/debug/context-budget, provider/model, generation, credential, retrieval/vectorization, archive/import, plugin shim, build artifact, protected core file, content-mode, minors/underage, or safety-bypass behavior changes occur.

## Verification Plan

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase146-scene-inspect-surface/design.md --require doc_type --require status --require feature`
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-06-hermes-tavern-phase146-scene-inspect-surface/checklist.yaml`
- `git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime.py src/hermes_tavern/db.py src/hermes_tavern/db_novel.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/importers plugins build/lib`
- `git diff --check`

## S2 Acceptance / Writeback

S2 is controller-owned after S1 verification. It may update only the Phase 146
CodeStable artifacts plus architecture/root design docs to describe the current
read-only scene inspect surface. S2 must not edit source, tests, README, plugin
shims, build artifacts, or protected core files.

Architecture/root design writeback should add only:

- `/rp scene inspect <scene-id>` in current command-surface lists.
- A note that scene inspection reads one existing `novel_scenes` row through the
  existing `get_scene(scene_id)` helper.
- The preserved boundaries: no schema, ordering, scene mutation, scene start/linking,
  prompt/provider/generation/retrieval/vectorization/credential/content-mode,
  minors/underage, or safety-bypass behavior changes.

## Risks / Rollback

Risk: users may infer this adds scene editing or reordering. Mitigation: keep command
text, README text, and tests strictly inspect-only.

Risk: scene output may become too large for mobile. Mitigation: use the existing
mobile preview helper for summary text and keep linked-session output bounded.

Rollback is simple: remove the scene inspect branch/helper function, generated help
literal, README literal, and focused tests. No schema or data rollback is needed.