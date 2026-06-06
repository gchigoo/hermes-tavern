---
doc_type: feature-design
feature: "2026-06-06-hermes-tavern-phase145-chapter-inspect-surface"
status: approved
date: "2026-06-06"
summary: >
  Phase 145 plans a read-only /rp chapter inspect <chapter-id> surface for
  existing novel_chapters rows, using the existing chapter getter and preserving
  schema, ordering, summary mutation, prompt, provider, generation, retrieval,
  credentials, safety behavior, and protected core files.
tags: [hermes-tavern, chapter, command-surface, read-only, offline]
created: "2026-06-06"
updated: "2026-06-06"
owner: codestable-cron
---
# Chapter Inspect Surface

## Background

Current CodeStable history is accepted through Phase 144. The recent accepted
inspect-surface family added single-row inspection for canon and timeline rows.
The base novel hierarchy still has `/rp chapter create/list` and `/rp chapter
summary ...`, but no read-only command that displays one chapter row and its
basic metadata.

This leaves chapter rows less inspectable than nearby metadata families even
though `TavernStore.get_chapter(chapter_id)` already exists.

## Scope

Add one read-only chapter inspection surface:

- `/rp chapter inspect <chapter-id>` routes under the existing chapter command
  family in `runtime_novel.py`.
- The command uses the existing `runtime.store.get_chapter(chapter_id)` helper.
- Generated `/rp help` and README Core commands include the new chapter inspect
  literal.
- Focused runtime/help/README tests cover success, malformed ids, missing rows,
  and unchanged chapter list/summary behavior.

## Non-goals / Boundaries

This phase does not add chapter update, delete, renumbering, reparenting, archive
import/export, bulk export changes, prompt/debug/context-budget injection,
provider/model routing, generation, retrieval/vectorization, credential handling,
content-mode behavior, automatic extraction, minors/underage handling, or provider
safety bypass behavior.

Do not edit `run_agent.py`, `cli.py`, `gateway/run.py`, `src/hermes_tavern/runtime.py`,
`src/hermes_tavern/db.py`, `src/hermes_tavern/db_novel.py`, prompt/provider/generation
files, importer files, `plugins/**`, or `build/lib/**`.

## Proposed design

The noun layer already exists: `novel_chapters(id, project_id, title,
chapter_number, summary, status, created_at, updated_at)`. This slice does not
create tables, alter indexes, mutate rows, or change `list_chapters(project_id)`
ordering.

The orchestration layer follows the accepted canon/timeline inspect shape:

- `/rp chapter inspect <chapter-id>`
- `TAVERN_COMMAND_TABLE["chapter"]`
- `TavernRuntime._chapter_command`
- `runtime_novel.chapter_command`
- new `chapter_inspect`
- existing `TavernStore.get_chapter`

The command output should be compact and bounded. It should include chapter id,
project id, chapter number, title, status, and a mobile-bounded summary preview
or an explicit not-set marker. Missing, malformed, non-positive, and extra
arguments should return the chapter usage string. Missing rows should return a
bounded not-found message.

No micro-refactor is needed. `runtime_novel.py` already owns the chapter command
family, and `commands.py` already owns generated help. This is a small family-local
extension.

## Acceptance criteria

1. `/rp chapter inspect <chapter-id>` returns bounded details for one existing chapter row.
2. Malformed ids, missing ids, non-positive ids, and extra args return the chapter usage string.
3. A missing chapter row returns a bounded not-found message without exceptions.
4. Generated help and README Core commands include `/rp chapter inspect <chapter-id>`.
5. Existing `/rp chapter list [project-id]` ordering and `/rp chapter summary ...` behavior remain unchanged.
6. No schema, prompt/debug/context-budget, provider/model, generation, credential, retrieval/vectorization, archive/import, plugin shim, build artifact, protected core file, or safety behavior changes occur.

## Verification plan

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`

## Risks / rollback

Risk: users may infer this adds chapter editing or renumbering. Mitigation: keep
command text, README text, and tests strictly inspect-only.

Risk: chapter output may become too large for mobile. Mitigation: use the existing
mobile preview helper for summary text.

Rollback is simple: remove the chapter inspect branch/helper function, generated
help literal, README literal, and focused tests. No schema or data rollback is needed.
