---
feature: 2026-05-22-hermes-tavern-phase21-persona-v1
summary: Add SillyTavern-like user personas as session-scoped prompt modules for Hermes Tavern.
tags: [hermes-tavern, persona, prompt, sqlite, runtime]
---

# Hermes Tavern Phase 21: Persona v1

## Goal

Add a narrow Persona v1 feature: imported user personas can be bound to a single active Tavern session and injected into the prompt as `persona:<name>`.

## Scope

- SQLite `personas` table.
- Guarded `sessions.persona_id` migration.
- Store helpers: `save_persona`, `list_personas`, `count_personas`, `get_persona`, `set_session_persona`.
- Runtime commands:
  - `/rp persona import <file>`
  - `/rp persona list [limit] [page]`
  - `/rp persona inspect <persona>`
  - `/rp persona use <persona>`
  - `/rp persona clear`
  - `/rp persona debug`
- Import JSON and raw text persona files.
- Preserve sanitized `raw_json` and `source_path` in the DB.
- Keep mobile-safe output and never print raw JSON.
- Use existing macro expansion by passing persona content through `PromptCompiler`.

## Non-Goals

- Persona editing or deletion.
- Global/default persona selection.
- Network calls or live model changes.
- New macro semantics.

## Design

Personas are first-class imported assets rather than preset modules. A session may reference at most one persona through `sessions.persona_id`. During prompt compilation, `TavernRuntime._session_prompt_modules()` appends the active persona as a `PromptModule`:

```text
name: persona:<persona name>
role: system
position: before_char
content: imported persona content
```

The compiler already macro-expands prompt module content, so `{{user}}`, `{{char}}`, and other Phase 20 macros work without a second expansion path.

## Data Model

```sql
personas(id, name, content, raw_json, source_path, created_at)
sessions.persona_id
```

`raw_json` is sanitized on import to remove secret-like keys. Runtime command output uses only summaries, previews, counts, IDs, and source path. It never dumps `raw_json`.

## Acceptance

- Existing DBs migrate with `personas` and `sessions.persona_id`.
- JSON personas and raw text personas import successfully.
- Personas resolve by full id, id prefix, or exact name.
- `/rp persona list` paginates.
- `/rp persona inspect` is mobile-safe and does not print raw JSON.
- `/rp persona use` binds only the active session.
- `/rp persona clear` removes prompt injection.
- `/rp debug prompt` and active generation include `persona:<name>` only when bound.
