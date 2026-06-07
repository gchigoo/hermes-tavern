---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase153-session-json-export"
date: "2026-06-07"
summary: >
  Phase 153 adds one bounded /rp session export <id> JSON export command for any
  stored session (not just the active one), following the Phase 149–152 export
  pattern. Resolves session by ID prefix, exports all messages as a JSON file
  under a profile-safe path, and returns file: plus quoted MEDIA:"<path>".
  No schema, prompt, provider, generation, content-mode, or safety behavior
  changes.
tags: [hermes-tavern, session, offline, export, json]
owner: codestable-cron
---

# Phase 153: Session JSON Export by ID

## Background

Phases 149–152 added individual JSON export commands for cards, lorebooks,
presets, and personas. Each exports one stored asset to a profile-safe local
JSON file and returns `file:` plus quoted `MEDIA:"<path>"`. The existing
`/rp export [markdown|st-json]` (Phase 23) already exports the *active*
session, but there is no way to export a specific stored session by ID
without first switching to it.

Current session surface already has `/rp sessions [all] [limit] [page]`
listing sessions with short IDs, and `/rp switch <id>` to restore them.
`TavernStore.list_sessions_by_id_prefix_for_scope(...)` resolves session
IDs by prefix. `TavernStore.get_messages_page(...)` provides paginated
message access. The missing parity surface is a direct session JSON export
by ID.

## Scope

Add one nested command:

- `/rp session export <id>`
- Resolve `<id>` through existing
  `list_sessions_by_id_prefix_for_scope(...)`, rejecting ambiguous matches.
- Read all session messages via `get_messages_page(...)` in paginated loops.
- Build a JSON export payload matching the existing st-json export format
  from `runtime_lifecycle.export()` (session metadata + messages array).
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "sessions"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change session lifecycle (start/end/pause/resume/switch/archive/clone),
the existing `/rp export [markdown|st-json]` active-session export,
session schema/index/migration code, prompt compiler, provider/model routing,
generation settings, credentials, content-mode, retrieval/vectorization,
project archive, plugin registration, gateway/core files, or build artifacts.

This phase does not implement bulk session export, session import,
session merge, session message search, or any other session editing tooling.

## Current State

Noun layer:

- `sessions(id, session_key, scope_key, card_id, status, title, preset_id,
  lorebook_id, persona_id, content_mode, note_text, ..., created_at, updated_at)`
  stores session metadata.
- `messages(id, session_id, role, content, created_at, metadata_json)` stores
  per-session messages.
- `TavernStore.list_sessions_by_id_prefix_for_scope(...)` resolves session IDs.
- `TavernStore.get_messages_page(session_id, limit, offset)` provides paginated
  message access.
- `TavernStore.get_card(...)`, `TavernStore.get_preset(...)`,
  `TavernStore.get_lorebook(...)` provide asset name resolution for export
  metadata.
- `runtime_sessions.py` owns nested session subcommands.
- `runtime_lifecycle.py` owns the active-session `export()` function that
  provides the JSON payload shape to match.
- `commands.py` owns generated `/rp help` literals.
- README Core commands mirror the public command surface.

Change:

- Add an `export` branch to `session_command(...)` in `runtime_sessions.py`.
- Add a local helper function in `runtime_sessions.py` for the export logic
  (`session_export`), reusing the existing `list_sessions_by_id_prefix_for_scope`
  resolver and `get_messages_page` reader.
- Reuse the existing st-json payload structure from `runtime_lifecycle.export()`
  for JSON shape consistency.
- Keep export read-only against Tavern data tables; only the local export file
  is created.

Flow:

```text
/rp session export <id>
  -> TAVERN_COMMAND_TABLE["session"]
  -> runtime_sessions.session_command
  -> session_export
  -> list_sessions_by_id_prefix_for_scope(scope_key, id_prefix, include_all=True, limit=3)
  -> reject if 0 or >1 match
  -> get_messages_page(session["id"], 200, offset) loop
  -> resolve card/preset/lorebook names for metadata
  -> write get_hermes_home()/plugins/hermes-tavern/exports/sessions/session_<id>.json
  -> return file: and MEDIA:"<path>"
```

## Export Payload Format

Match the existing st-json export shape from `runtime_lifecycle.export()`:

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO timestamp>",
  "session_title": "<title>",
  "card_name": "<card name>",
  "content_mode": "<safe|adult-fiction>",
  "preset_name": "<preset name or 'none'>",
  "lorebook_name": "<lorebook name or 'none'>",
  "message_count": <N>,
  "messages": [
    {"role": "user|assistant", "content": "...", "swipes": [...], "active_swipe": 0}
  ]
}
```

When stored card data is available, include a `"card"` top-level key with the
parsed card JSON (same as current st-json export).

When session messages include `metadata_json` with swipe data, include
`swipes` and `active_swipe` fields (same as current st-json export).

## Structure Health

No micro-refactor is required.

`runtime_sessions.py` is the established owner for nested session command
orchestration and is small enough for one bounded export helper cluster.
`commands.py`, README, and the existing session/commands/docs tests are
direct help/docs surfaces. No new module or directory is needed.

## S1 Allowed Files

- `src/hermes_tavern/runtime_sessions.py`
- `src/hermes_tavern/commands.py`
- `README.md`
- `tests/test_hermes_tavern_sessions.py`
- `tests/test_hermes_tavern_commands.py`
- `tests/test_hermes_tavern_readme_docs.py`

## S1 Prohibited Files

- `run_agent.py`
- `cli.py`
- `gateway/run.py`
- `src/hermes_tavern/runtime.py`
- `src/hermes_tavern/runtime_lifecycle.py`
- `src/hermes_tavern/db.py`
- `src/hermes_tavern/db_novel.py`
- `src/hermes_tavern/prompt.py`
- `src/hermes_tavern/runtime_prompt_modules.py`
- `src/hermes_tavern/model_router.py`
- `src/hermes_tavern/provider_bridge.py`
- `src/hermes_tavern/adapters.py`
- `src/hermes_tavern/runtime_generation.py`
- `src/hermes_tavern/runtime_assets.py`
- `src/hermes_tavern/runtime_lore.py`
- `src/hermes_tavern/runtime_persona.py`
- `src/hermes_tavern/runtime_presets.py`
- `src/hermes_tavern/runtime_novel.py`
- `src/hermes_tavern/importers/**`
- `plugins/**`
- `build/lib/**`

## S1 Implementation Plan

1. Add `/rp session export <id>` dispatch and usage in `runtime_sessions.py`.
2. Use `list_sessions_by_id_prefix_for_scope(...)` for ID resolution; reject
   ambiguous (>1 match) and not-found (0 matches).
3. Read all messages via `get_messages_page(...)` in 200-row pages.
4. Resolve card/preset/lorebook names from stored assets for JSON metadata.
5. Build JSON payload matching the existing st-json export shape.
6. Use `get_hermes_home()` for the session export directory; do not hard-code
   `~/.hermes`.
7. Write UTF-8 JSON file and return `file:` plus quoted `MEDIA:"<path>"`.
8. Add help and README Core command literals.
9. Add focused tests: export by ID, not-found, ambiguous match, session
   with messages, session without messages, path containment, quoted paths
   with spaces, and no session/message mutation.

## Acceptance Criteria

1. `/rp session export <id>` writes one UTF-8 JSON file under
   `get_hermes_home()/plugins/hermes-tavern/exports/sessions`.
2. Export resolves session by ID prefix; rejects ambiguous matches (>1).
3. Export works for sessions with messages, including swipe metadata.
4. Export works for sessions with zero messages (empty messages array).
5. Export includes card/preset/lorebook name resolution.
6. The response includes `file:` and quoted `MEDIA:"<path>"`, including paths
   with spaces.
7. Sanitized filenames remain inside the session export directory.
8. Generated help and README Core commands include `/rp session export <id>`.
9. Session/message rows are not mutated by export.
10. No schema, prompt, provider/model, generation, retrieval/vectorization,
    credential, content-mode, project archive, plugin, build, minors/underage,
    or safety-bypass behavior changes occur.

## Verification Plan

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_sessions.py src/hermes_tavern/commands.py tests/test_hermes_tavern_sessions.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_sessions.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime.py src/hermes_tavern/runtime_lifecycle.py src/hermes_tavern/db.py src/hermes_tavern/db_novel.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/runtime_assets.py src/hermes_tavern/runtime_lore.py src/hermes_tavern/runtime_persona.py src/hermes_tavern/runtime_presets.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/importers plugins build/lib`
- `git diff --check`
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-07-hermes-tavern-phase153-session-json-export/design.md --require doc_type --require status --require feature`
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-07-hermes-tavern-phase153-session-json-export/checklist.yaml`

## Risks / Rollback

Risk: ID prefix resolution may return ambiguous matches for short prefixes.
Mitigation: reject when list_sessions_by_id_prefix_for_scope returns >1 match;
require a longer prefix (same UX as `/rp switch`).

Risk: Export payload shape differs from existing st-json format.
Mitigation: reuse the exact same key structure and content rules as
`runtime_lifecycle.export()` for format compatibility.

Rollback is limited to removing the session export branch/helpers, the
help/README literal, and focused tests. No DB migration or data rollback is
needed.

## S2 Later Tick

S2 is a docs/status acceptance and writeback slice for a later cron tick only.
It should rerun S1 verification, create the acceptance report, then update
architecture/root-design current-state docs and finalize checklist/design status.
S2 must not edit source, tests, README, gateway/core, plugin, provider, prompt,
schema, importer, generation, content-mode, or build files.
